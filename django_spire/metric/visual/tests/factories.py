from __future__ import annotations

from decimal import Decimal

from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.statistic.constants import StatisticIntervalChoices
from django_spire.metric.domain.statistic.models import Statistic, StatisticGroup
from django_spire.metric.visual.models import Visual, VisualCondition


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
) -> Statistic:
    return Statistic.objects.create(group=group, name=name, interval=interval)


def create_test_visual(
    statistic: Statistic,
    name: str = 'test_visual',
    reference: str = '',
    kind: str = 'indicator',
    with_conditions: bool = True,
    target: Decimal = Decimal(100),
    tolerance: Decimal = Decimal(10),
) -> Visual:
    visual = Visual.objects.create(name=name, statistic=statistic, reference=reference, kind=kind)

    if with_conditions:
        visual.services.factory.create_default_conditions(target=target, tolerance=tolerance)

    visual.refresh_from_db()
    return visual


def create_test_condition(
    visual: Visual,
    state: str = 'green',
    operator: str = 'gt',
    target: Decimal = Decimal(100),
    tolerance: Decimal = Decimal(0),
    order: int = 0,
) -> VisualCondition:
    return VisualCondition.objects.create(
        visual=visual,
        state=state,
        operator=operator,
        target=target,
        tolerance=tolerance,
        order=order,
    )
