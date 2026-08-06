from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_spire.metric.domain.statistic.services.factory_service import (
    StatisticFactoryService,
    StatisticGroupFactoryService,
    StatisticValueFactoryService,
)
from django_spire.metric.domain.statistic.services.intelligence_service import (
    StatisticGroupIntelligenceService,
    StatisticIntelligenceService,
    StatisticValueIntelligenceService,
)
from django_spire.metric.domain.statistic.services.processor_service import (
    StatisticGroupProcessorService,
    StatisticProcessorService,
    StatisticValueProcessorService,
)
from django_spire.metric.domain.statistic.services.transformation_service import (
    StatisticGroupTransformationService,
    StatisticTransformationService,
    StatisticValueTransformationService,
)

if TYPE_CHECKING:
    from django_spire.metric.domain.statistic.models import (
        Statistic,
        StatisticGroup,
        StatisticValue,
    )


class StatisticService(BaseDjangoModelService['Statistic']):
    obj: Statistic

    intelligence = StatisticIntelligenceService()
    processor = StatisticProcessorService()
    factory = StatisticFactoryService()
    transformation = StatisticTransformationService()


class StatisticGroupService(BaseDjangoModelService['StatisticGroup']):
    obj: StatisticGroup

    intelligence = StatisticGroupIntelligenceService()
    processor = StatisticGroupProcessorService()
    factory = StatisticGroupFactoryService()
    transformation = StatisticGroupTransformationService()


class StatisticValueService(BaseDjangoModelService['StatisticValue']):
    obj: StatisticValue

    intelligence = StatisticValueIntelligenceService()
    processor = StatisticValueProcessorService()
    factory = StatisticValueFactoryService()
    transformation = StatisticValueTransformationService()
