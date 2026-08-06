from __future__ import annotations


from django_spire.metric.domain.models import Domain
from django_spire.metric.domain.statistic.constants import StatisticIntervalChoices
from django_spire.metric.domain.statistic.models import Statistic, StatisticGroup


def create_test_domain(name: str = 'test_domain') -> Domain:
    return Domain.objects.create(name=name)


def create_test_statistic_group(
    domain: Domain, name: str = 'test_statistic_group', description: str = 'group description'
) -> StatisticGroup:
    return StatisticGroup.objects.create(domain=domain, name=name, description=description)


def create_test_statistic(
    group: StatisticGroup,
    name: str = 'test_statistic',
    interval: str = StatisticIntervalChoices.DAILY,
) -> Statistic:
    return Statistic.objects.create(group=group, name=name, interval=interval)
