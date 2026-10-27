from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django_spire.conf import settings as spire_settings
from django_spire.contrib.utils import get_object_from_module_string
from django_spire.exceptions import DjangoSpireConfigurationError, DjangoSpireInvalidClassStringError
from django_spire.metric.domain.statistic.constants import StatisticIntervalChoices, StatisticValueTypeChoices
from django_spire.metric.key_utils import KEY_MAX_LENGTH, object_key, validate_local_key
from django_spire.metric.specs import DomainSpec, StatisticGroupSpec, StatisticSpec, SubDomainSpec

if TYPE_CHECKING:
    from django_spire.metric.metric import Metric
    from django_spire.metric.summary import BuildSummary


def _sub_domain_key(domain_key: str, sub_domain: SubDomainSpec) -> str:
    return object_key(domain_key, sub_domain.key)


def _statistic_group_key(domain_key: str, statistic_group: StatisticGroupSpec) -> str:
    return object_key(domain_key, statistic_group.key)


def _statistic_key(domain_key: str, statistic_group: StatisticGroupSpec, statistic: StatisticSpec) -> str:
    return object_key(domain_key, statistic_group.key, statistic.key)


def _validate_spec_name(name: Any, kind: str) -> None:
    if not isinstance(name, str) or not name:
        message = f'{kind} name must be a non-empty string, got {name!r}'
        raise ValueError(message)


def _report_deleted(summary: BuildSummary, path: str, check: bool) -> None:
    if check:
        summary.missing.append(path)
    else:
        summary.errors.append(f'{path}: exists but is deleted; undelete it or drop it from the spec')


def _sync_fields(obj: Any, values: dict[str, Any], *, save: bool = True) -> bool:
    changed = [name for name, value in values.items() if getattr(obj, name) != value]
    if not changed:
        return False
    if save:
        for name, value in values.items():
            setattr(obj, name, value)
        obj.save(update_fields=changed)
    return True


def _count_sync(summary: BuildSummary, obj: Any, values: dict[str, Any], path: str, check: bool) -> None:
    if _sync_fields(obj, values, save=not check):
        if check:
            summary.errors.append(f'{path}: drifts from spec; run metric_build to sync')
        else:
            summary.updated += 1
        return
    summary.unchanged += 1


def _resolve_remote_target(name: str) -> tuple[str, str]:
    targets = spire_settings.DJANGO_SPIRE_METRIC_REMOTE_TARGETS or {}
    if name in targets:
        target = targets[name]
        url = target.get('url', '')
        api_key = target.get('api_key', '')
        if not url or not api_key:
            message = f'Remote metric target {name!r} is missing url or api_key'
            raise DjangoSpireConfigurationError(message)
        return url, api_key

    url = spire_settings.DJANGO_SPIRE_REMOTE_API_URL
    api_key = spire_settings.DJANGO_SPIRE_REMOTE_API_KEY
    if not url or not api_key:
        message = (
            f'Remote metric target {name!r} is not configured; set '
            'DJANGO_SPIRE_METRIC_REMOTE_TARGETS or DJANGO_SPIRE_REMOTE_API_URL/KEY'
        )
        raise DjangoSpireConfigurationError(message)

    return url, api_key


def _validate_sub_domain_spec(
    cls_name: str, domain: DomainSpec, sub_domain: Any, seen_local_keys: set[str], seen_stored_keys: set[str]
) -> None:
    if not isinstance(sub_domain, SubDomainSpec):
        message = 'subdomains entries must be Metric.SubDomain specs'
        raise TypeError(message)
    validate_local_key(sub_domain.key, 'sub-domain')
    _validate_spec_name(sub_domain.name, 'sub-domain')
    if sub_domain.key in seen_local_keys:
        message = f'domain {domain.key!r} declares duplicate sub-domain key {sub_domain.key!r}'
        raise ValueError(message)
    seen_local_keys.add(sub_domain.key)
    stored_key = _sub_domain_key(domain.key, sub_domain)
    if len(stored_key) > KEY_MAX_LENGTH:
        message = f'sub-domain key {stored_key!r} exceeds {KEY_MAX_LENGTH} characters'
        raise ValueError(message)
    if stored_key in seen_stored_keys:
        message = f'{cls_name} declares duplicate sub-domain key {stored_key!r}'
        raise ValueError(message)
    seen_stored_keys.add(stored_key)


def _validate_statistic_spec(
    cls_name: str,
    domain: DomainSpec,
    statistic_group: StatisticGroupSpec,
    statistic: Any,
    *,
    seen_local_keys: set[str],
    seen_stored_keys: set[str],
) -> None:
    if not isinstance(statistic, StatisticSpec):
        message = 'statistics entries must be Metric.Statistic specs'
        raise TypeError(message)
    validate_local_key(statistic.key, 'statistic')
    _validate_spec_name(statistic.name, 'statistic')
    if statistic.interval and statistic.interval not in StatisticIntervalChoices.values:
        message = f'statistic {statistic.key!r} has unknown interval {statistic.interval!r}'
        raise ValueError(message)
    if statistic.value_type and statistic.value_type not in StatisticValueTypeChoices.values:
        message = f'statistic {statistic.key!r} has unknown value_type {statistic.value_type!r}'
        raise ValueError(message)
    if statistic.key in seen_local_keys:
        message = f'statistic group {statistic_group.key!r} declares duplicate statistic key {statistic.key!r}'
        raise ValueError(message)
    seen_local_keys.add(statistic.key)
    stored_key = _statistic_key(domain.key, statistic_group, statistic)
    if len(stored_key) > KEY_MAX_LENGTH:
        message = f'statistic key {stored_key!r} exceeds {KEY_MAX_LENGTH} characters'
        raise ValueError(message)
    if stored_key in seen_stored_keys:
        message = f'{cls_name} declares duplicate statistic key {stored_key!r}'
        raise ValueError(message)
    seen_stored_keys.add(stored_key)


def _validate_statistic_group_spec(
    cls_name: str, domain: DomainSpec, statistic_group: Any, seen_local_keys: set[str], seen_statistic_keys: set[str]
) -> None:
    if not isinstance(statistic_group, StatisticGroupSpec):
        message = 'statistic_groups entries must be Metric.StatisticGroup specs'
        raise TypeError(message)
    validate_local_key(statistic_group.key, 'statistic group')
    _validate_spec_name(statistic_group.name, 'statistic group')
    if statistic_group.key in seen_local_keys:
        message = f'domain {domain.key!r} declares duplicate statistic group key {statistic_group.key!r}'
        raise ValueError(message)
    seen_local_keys.add(statistic_group.key)
    stored_key = _statistic_group_key(domain.key, statistic_group)
    if len(stored_key) > KEY_MAX_LENGTH:
        message = f'statistic group key {stored_key!r} exceeds {KEY_MAX_LENGTH} characters'
        raise ValueError(message)

    seen_statistic_local_keys: set[str] = set()
    for statistic in statistic_group.statistics:
        _validate_statistic_spec(
            cls_name,
            domain,
            statistic_group,
            statistic,
            seen_local_keys=seen_statistic_local_keys,
            seen_stored_keys=seen_statistic_keys,
        )


def _validate_domain_spec(
    cls_name: str,
    domain: Any,
    seen_domain_keys: set[str],
    seen_sub_domain_keys: set[str],
    seen_statistic_keys: set[str],
) -> None:
    if not isinstance(domain, DomainSpec):
        message = f'{cls_name}.domains entries must be Metric.Domain specs'
        raise TypeError(message)
    validate_local_key(domain.key, 'domain')
    _validate_spec_name(domain.name, 'domain')
    if domain.key in seen_domain_keys:
        message = f'{cls_name} declares duplicate domain key {domain.key!r}'
        raise ValueError(message)
    seen_domain_keys.add(domain.key)

    seen_sub_domain_local_keys: set[str] = set()
    for sub_domain in domain.subdomains:
        _validate_sub_domain_spec(cls_name, domain, sub_domain, seen_sub_domain_local_keys, seen_sub_domain_keys)

    seen_statistic_group_local_keys: set[str] = set()
    for statistic_group in domain.statistic_groups:
        _validate_statistic_group_spec(
            cls_name, domain, statistic_group, seen_statistic_group_local_keys, seen_statistic_keys
        )


def discover_metric_registries() -> list[type[Metric]]:
    from django_spire.metric.metric import Metric  # noqa: PLC0415

    registries: list[type[Metric]] = []

    for class_string in spire_settings.DJANGO_SPIRE_METRIC_REGISTRY or []:
        registry_class = get_object_from_module_string(class_string)
        if not isinstance(registry_class, type) or not issubclass(registry_class, Metric):
            message = f'Metric registry {class_string} must be a subclass of Metric'
            raise DjangoSpireInvalidClassStringError(message)
        registries.append(registry_class)

    return registries
