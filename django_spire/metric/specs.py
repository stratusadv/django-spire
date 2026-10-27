from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.db import transaction

from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.statistic.models import Statistic, StatisticGroup

if TYPE_CHECKING:
    from typing import Any

    from django_spire.metric.summary import BuildSummary


@dataclass(frozen=True)
class SubDomainSpec:
    key: str
    name: str
    description: str = ''

    def build(self, domain: Domain, *, check: bool, summary: BuildSummary) -> None:
        from django_spire.metric.utils import (  # noqa: PLC0415
            _count_sync,
            _report_deleted,
            _sub_domain_key,
        )

        stored_key = _sub_domain_key(domain.key, self)
        path = f'{domain.key}/{self.key}'
        values = {'name': self.name, 'description': self.description}
        created = False
        sub_domain = SubDomain.objects.for_key(stored_key).first()

        if sub_domain is None:
            if check:
                summary.missing.append(path)
                return
            sub_domain, created = SubDomain.objects.get_or_create(domain=domain, key=stored_key, defaults=values)

        if created:
            summary.created += 1
            return

        if sub_domain.is_deleted:
            _report_deleted(summary, path, check)
            return

        _count_sync(summary, sub_domain, values, path, check)


@dataclass(frozen=True)
class StatisticSpec:
    key: str
    name: str
    interval: str = ''
    value_type: str = ''

    def build(
        self,
        domain: Domain,
        statistic_group: StatisticGroup,
        statistic_group_spec: StatisticGroupSpec,
        *,
        check: bool,
        summary: BuildSummary,
    ) -> None:
        from django_spire.metric.utils import (  # noqa: PLC0415
            _count_sync,
            _report_deleted,
            _statistic_key,
        )

        stored_key = _statistic_key(domain.key, statistic_group_spec, self)
        path = f'{domain.key}/{statistic_group_spec.key}/{self.key}'
        statistic = Statistic.objects.for_key(stored_key).first()

        created = False
        if statistic is None:
            if check:
                summary.missing.append(path)
                return
            values: dict[str, Any] = {'group': statistic_group, 'name': self.name}
            if self.interval:
                values['interval'] = self.interval
            if self.value_type:
                values['value_type'] = self.value_type
            statistic, created = Statistic.objects.get_or_create(key=stored_key, defaults=values)

        if created:
            summary.created += 1
            return

        if statistic.is_deleted:
            _report_deleted(summary, path, check)
            return

        sync_values: dict[str, Any] = {'name': self.name}
        if self.interval:
            sync_values['interval'] = self.interval
        if self.value_type:
            sync_values['value_type'] = self.value_type
        _count_sync(summary, statistic, sync_values, path, check)


@dataclass(frozen=True)
class StatisticGroupSpec:
    key: str
    name: str
    description: str = ''
    statistics: tuple[StatisticSpec, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, 'statistics', tuple(self.statistics))

    def build(self, domain: Domain, *, check: bool, summary: BuildSummary) -> None:
        from django_spire.metric.utils import (  # noqa: PLC0415
            _count_sync,
            _report_deleted,
            _statistic_group_key,
        )

        stored_key = _statistic_group_key(domain.key, self)
        path = f'{domain.key}/{self.key}'
        values = {'name': self.name, 'description': self.description}
        created = False
        statistic_group = StatisticGroup.objects.for_key(stored_key).first()

        if statistic_group is None:
            if check:
                summary.missing.append(path)
                return
            statistic_group, created = StatisticGroup.objects.get_or_create(
                domain=domain, key=stored_key, defaults=values
            )

        if created:
            summary.created += 1
        else:
            if statistic_group.is_deleted:
                _report_deleted(summary, path, check)
                return
            _count_sync(summary, statistic_group, values, path, check)

        for statistic_spec in self.statistics:
            statistic_spec.build(domain, statistic_group, self, check=check, summary=summary)


@dataclass(frozen=True)
class DomainSpec:
    key: str
    name: str
    description: str = ''
    sub_domain_name: str = ''
    subdomains: tuple[SubDomainSpec, ...] = ()
    statistic_groups: tuple[StatisticGroupSpec, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, 'subdomains', tuple(self.subdomains))
        object.__setattr__(self, 'statistic_groups', tuple(self.statistic_groups))

    def build(self, *, check: bool, summary: BuildSummary) -> None:
        from django_spire.metric.utils import _count_sync, _report_deleted  # noqa: PLC0415

        values = {'name': self.name, 'description': self.description, 'sub_domain_name': self.sub_domain_name}

        try:
            with transaction.atomic():
                created = False
                domain = Domain.objects.for_key(self.key).first()

                if domain is None:
                    if check:
                        summary.missing.append(self.key)
                        return
                    domain, created = Domain.objects.get_or_create(key=self.key, defaults=values)

                if created:
                    summary.created += 1
                else:
                    if domain.is_deleted:
                        _report_deleted(summary, self.key, check)
                        return
                    _count_sync(summary, domain, values, self.key, check)

                for sub_domain_spec in self.subdomains:
                    sub_domain_spec.build(domain, check=check, summary=summary)

                for statistic_group_spec in self.statistic_groups:
                    statistic_group_spec.build(domain, check=check, summary=summary)
        except Exception as error:
            summary.errors.append(f'{self.key}: {error}')
