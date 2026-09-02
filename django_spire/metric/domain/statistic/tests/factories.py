from __future__ import annotations

from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.statistic.constants import (
    StatisticIntervalChoices,
    StatisticValueTypeChoices,
)
from django_spire.metric.domain.statistic.models import Statistic, StatisticGroup


def create_test_domain(name: str = 'test_domain') -> Domain:
    return Domain.objects.create(name=name)


def create_test_subdomain(domain: Domain, name: str = 'test_subdomain') -> SubDomain:
    return domain.subdomains.create(name=name)


def create_test_statistic_group(
    domain: Domain, name: str = 'test_statistic_group', description: str = 'group description'
) -> StatisticGroup:
    return StatisticGroup.objects.create(domain=domain, name=name, description=description)


def create_test_statistic(
    group: StatisticGroup,
    name: str = 'test_statistic',
    interval: str = StatisticIntervalChoices.DAILY,
    value_type: str = StatisticValueTypeChoices.NUMBER,
) -> Statistic:
    return Statistic.objects.create(
        group=group, name=name, interval=interval, value_type=value_type
    )
