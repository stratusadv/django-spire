from __future__ import annotations

import logging
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from decimal import Decimal
from enum import StrEnum

from django.db import connections, models
from requests.exceptions import RequestException

from django_spire.conf import settings as spire_settings
from django_spire.contrib.rest.connector.exceptions import RestConnectorError, RestConnectorTimeoutException
from django_spire.metric.domain.statistic.models import Statistic
from django_spire.metric.domain.statistic.services.rest_connector import SpireMetricRestConnector
from django_spire.metric.specs import DomainSpec, StatisticGroupSpec, StatisticSpec, SubDomainSpec
from django_spire.metric.summary import BuildSummary
from django_spire.metric.utils import (
    _resolve_remote_target,
    _statistic_group_key,
    _statistic_key,
    _sub_domain_key,
    _validate_domain_spec,
    discover_metric_registries,  # noqa: F401
)

logger = logging.getLogger(__name__)


_REMOTE_API_PATH = 'api/v1/metric/domain/statistic'

_RECORD_EXECUTOR: ThreadPoolExecutor | None = None
_RECORD_EXECUTOR_LOCK = threading.Lock()


def _record_executor() -> ThreadPoolExecutor:
    global _RECORD_EXECUTOR  # noqa: PLW0603
    if _RECORD_EXECUTOR is None:
        with _RECORD_EXECUTOR_LOCK:
            if _RECORD_EXECUTOR is None:
                workers = spire_settings.DJANGO_SPIRE_METRIC_RECORD_WORKERS
                _RECORD_EXECUTOR = ThreadPoolExecutor(
                    max_workers=max(workers or 2, 1), thread_name_prefix='django-spire-metric-record'
                )
    return _RECORD_EXECUTOR


class _RecordHandle:
    def __init__(self, future: Future) -> None:
        self._future = future

    def join(self, timeout: float | None = None) -> None:
        self._future.result(timeout=timeout)


class Metric:
    """
    Declarative metric structure. Subclass it, declare domains, sub-domains,
    statistic groups, and statistics with the nested spec constructors, then
    build() syncs the structure, check() validates it, and record() writes
    values local or to the configured remote target.
    """

    class Target(StrEnum):
        LOCAL = 'local'
        REMOTE = 'remote'

    Domain = DomainSpec
    SubDomain = SubDomainSpec
    StatisticGroup = StatisticGroupSpec
    Statistic = StatisticSpec

    target: Target = Target.LOCAL
    remote_target: str | None = None
    domains: list[DomainSpec] = []

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        if not isinstance(cls.target, cls.Target):
            message = f'{cls.__name__}.target must be a Metric.Target, got {cls.target!r}'
            raise TypeError(message)

        if cls.target is cls.Target.REMOTE and (not isinstance(cls.remote_target, str) or not cls.remote_target):
            message = f'{cls.__name__}.remote_target must be a non-empty string when target is Target.REMOTE'
            raise ValueError(message)

        if not isinstance(cls.domains, (list, tuple)) or not cls.domains:
            message = f'{cls.__name__}.domains must be a non-empty list of Metric.Domain'
            raise ValueError(message)

        seen_domain_keys: set[str] = set()
        seen_sub_domain_keys: set[str] = set()
        seen_statistic_keys: set[str] = set()

        for domain in cls.domains:
            _validate_domain_spec(cls.__name__, domain, seen_domain_keys, seen_sub_domain_keys, seen_statistic_keys)

    @classmethod
    def build(cls, *, check: bool = False) -> BuildSummary:
        if cls.target is cls.Target.REMOTE:
            message = (
                f'{cls.__name__} targets a remote installation; run metric_build on that '
                'installation to build its structure. This registry can record() and '
                'check() against it.'
            )
            raise ValueError(message)

        return cls._build_local(check=check)

    @classmethod
    def check(cls) -> BuildSummary:
        if cls.target is cls.Target.REMOTE:
            return cls._check_remote()

        return cls._build_local(check=True)

    @classmethod
    def _build_local(cls, *, check: bool) -> BuildSummary:
        summary = BuildSummary()
        for domain_spec in cls.domains:
            domain_spec.build(check=check, summary=summary)
        return summary

    @classmethod
    def _check_remote(cls) -> BuildSummary:
        summary = BuildSummary()
        url, api_key = _resolve_remote_target(cls.remote_target)
        connector = SpireMetricRestConnector(base_url=url, api_key=api_key)

        for domain_spec in cls.domains:
            probe_statistic_key: str | None = None

            for statistic_group_spec in domain_spec.statistic_groups:
                for statistic_spec in statistic_group_spec.statistics:
                    stored_key = _statistic_key(domain_spec.key, statistic_group_spec, statistic_spec)
                    if not cls._remote_probe(connector, f'{_REMOTE_API_PATH}/{stored_key}/total'):
                        summary.missing.append(f'{domain_spec.key}/{statistic_group_spec.key}/{statistic_spec.key}')
                        continue
                    if probe_statistic_key is None:
                        probe_statistic_key = stored_key

            if domain_spec.subdomains and probe_statistic_key is None:
                summary.errors.append(f'{domain_spec.key}: no statistic reachable, sub-domains not checked')
                continue

            for sub_domain_spec in domain_spec.subdomains:
                stored_key = _sub_domain_key(domain_spec.key, sub_domain_spec)
                if not cls._remote_probe(
                    connector, f'{_REMOTE_API_PATH}/{probe_statistic_key}/total', params={'sub_domain_key': stored_key}
                ):
                    summary.missing.append(f'{domain_spec.key}/{sub_domain_spec.key}')

        return summary

    @staticmethod
    def _remote_probe(connector: SpireMetricRestConnector, path: str, params: dict[str, str] | None = None) -> bool:
        try:
            response = connector.get(path, params=params)
        except (RestConnectorError, RestConnectorTimeoutException, RequestException):
            return False
        return response.status_code == 200

    @classmethod
    def record(  # noqa: PLR0917
        cls,
        domain_key: str,
        sub_domain_key: str,
        statistic_group_key: str,
        statistic_key: str,
        reference: list[str],
        value: float | Decimal = 1,
        *,
        source_model: models.Model | None = None,
    ) -> _RecordHandle:
        domain_spec, statistic_group_spec, statistic_spec = cls._resolve_statistic(
            domain_key, statistic_group_key, statistic_key
        )

        sub_domain_spec = cls._resolve_sub_domain(domain_spec, sub_domain_key)
        stored_statistic_key = _statistic_key(domain_spec.key, statistic_group_spec, statistic_spec)
        stored_sub_domain_key = _sub_domain_key(domain_spec.key, sub_domain_spec)
        stored_reference = cls._join_reference(cls._postfix_reference(reference, source_model))

        future = _record_executor().submit(
            cls._record_dispatch, stored_statistic_key, stored_sub_domain_key, stored_reference, value
        )

        return _RecordHandle(future)

    @staticmethod
    def _postfix_reference(reference: list[str], model: models.Model | None) -> list[str]:
        if model is None:
            return reference
        if not isinstance(model, models.Model):
            message = 'source_model must be a Django model instance or None'
            raise TypeError(message)
        if model.pk is None:
            message = 'source_model must be a saved model instance'
            raise ValueError(message)
        return [*reference, f'{model._meta.app_label}.{model._meta.model_name}', str(model.pk)]

    @staticmethod
    def _join_reference(reference: list[str]) -> str:
        if not isinstance(reference, list):
            message = 'reference must be a list of strings, not a single string'
            raise TypeError(message)
        return ':'.join(reference)

    @classmethod
    def _record_dispatch(
        cls, stored_statistic_key: str, stored_sub_domain_key: str, reference: str, value: float | Decimal
    ) -> None:
        try:
            if cls.target is cls.Target.LOCAL:
                Statistic.record(stored_statistic_key, stored_sub_domain_key, reference, value)
                return

            url, api_key = _resolve_remote_target(cls.remote_target)
            connector = SpireMetricRestConnector(base_url=url, api_key=api_key)
            payload = {'reference': reference, 'sub_domain_key': stored_sub_domain_key, 'value': str(Decimal(value))}
            connector.record(stored_statistic_key, payload).json()
        except Exception:
            logger.exception(
                'Metric record failed for statistic %r (sub-domain %r)', stored_statistic_key, stored_sub_domain_key
            )
        finally:
            connections.close_all()

    @classmethod
    def stored_keys(cls) -> dict[str, set[str]]:
        domain_keys: set[str] = set()
        sub_domain_keys: set[str] = set()
        statistic_group_keys: set[str] = set()
        statistic_keys: set[str] = set()

        for domain in cls.domains:
            domain_keys.add(domain.key)
            for sub_domain in domain.subdomains:
                sub_domain_keys.add(_sub_domain_key(domain.key, sub_domain))
            for statistic_group in domain.statistic_groups:
                statistic_group_keys.add(_statistic_group_key(domain.key, statistic_group))
                for statistic in statistic_group.statistics:
                    statistic_keys.add(_statistic_key(domain.key, statistic_group, statistic))

        return {
            'domains': domain_keys,
            'subdomains': sub_domain_keys,
            'statistic_groups': statistic_group_keys,
            'statistics': statistic_keys,
        }

    @classmethod
    def _resolve_statistic(
        cls, domain_key: str, statistic_group_key: str, statistic_key: str
    ) -> tuple[DomainSpec, StatisticGroupSpec, StatisticSpec]:
        for domain_spec in cls.domains:
            if domain_spec.key != domain_key:
                continue
            for statistic_group_spec in domain_spec.statistic_groups:
                if statistic_group_spec.key != statistic_group_key:
                    continue
                for statistic_spec in statistic_group_spec.statistics:
                    if statistic_spec.key == statistic_key:
                        return domain_spec, statistic_group_spec, statistic_spec

        message = (
            f'No statistic declared for domain {domain_key!r}, statistic group '
            f'{statistic_group_key!r}, statistic {statistic_key!r} in {cls.__name__}'
        )
        raise ValueError(message)

    @classmethod
    def _resolve_sub_domain(cls, domain_spec: DomainSpec, key: str) -> SubDomainSpec:
        for sub_domain_spec in domain_spec.subdomains:
            if sub_domain_spec.key == key:
                return sub_domain_spec

        message = f'No sub-domain {key!r} declared on domain {domain_spec.key!r} in {cls.__name__}'
        raise ValueError(message)


Target = Metric.Target
