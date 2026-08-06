from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.metric.domain.statistic.models import (
        Statistic,
        StatisticGroup,
        StatisticValue,
    )


class StatisticGroupFactoryService(BaseDjangoModelService['StatisticGroup']):
    obj: StatisticGroup


class StatisticFactoryService(BaseDjangoModelService['Statistic']):
    obj: Statistic


class StatisticValueFactoryService(BaseDjangoModelService['StatisticValue']):
    obj: StatisticValue
