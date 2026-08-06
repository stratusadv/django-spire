from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.metric.domain.statistic.models import (
        Statistic,
        StatisticGroup,
        StatisticValue,
    )


class StatisticGroupIntelligenceService(BaseDjangoModelService['StatisticGroup']):
    obj: StatisticGroup


class StatisticIntelligenceService(BaseDjangoModelService['Statistic']):
    obj: Statistic


class StatisticValueIntelligenceService(BaseDjangoModelService['StatisticValue']):
    obj: StatisticValue
