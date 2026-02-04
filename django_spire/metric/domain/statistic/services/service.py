from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

from django_spire.metric.domain.statistic.services.factory_service import StatisticFactoryService
from django_spire.metric.domain.statistic.services.intelligence_service import StatisticIntelligenceService
from django_spire.metric.domain.statistic.services.processor_service import StatisticProcessorService
from django_spire.metric.domain.statistic.services.transformation_service import StatisticTransformationService

if TYPE_CHECKING:
    from django_spire.metric.domain.statistic.models import Statistic


class StatisticService(BaseDjangoModelService['Statistic']):
    obj: Statistic

    intelligence = StatisticIntelligenceService()
    processor = StatisticProcessorService()
    factory = StatisticFactoryService()
    transformation = StatisticTransformationService()
