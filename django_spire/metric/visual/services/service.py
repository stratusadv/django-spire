from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

from django_spire.metric.visual.services.factory_service import (
    VisualConditionFactoryService,
    VisualFactoryService,
)
from django_spire.metric.visual.services.intelligence_service import (
    VisualConditionIntelligenceService,
    VisualIntelligenceService,
)
from django_spire.metric.visual.services.processor_service import (
    VisualConditionProcessorService,
    VisualProcessorService,
)
from django_spire.metric.visual.services.transformation_service import (
    VisualConditionTransformationService,
    VisualTransformationService,
)

if TYPE_CHECKING:
    from django_spire.metric.visual.models import Visual, VisualCondition


class VisualService(BaseDjangoModelService['Visual']):
    obj: Visual

    intelligence = VisualIntelligenceService()
    processor = VisualProcessorService()
    factory = VisualFactoryService()
    transformation = VisualTransformationService()


class IndicatorVisualService(VisualService):
    obj: Visual


class LineChartVisualService(VisualService):
    obj: Visual


class BarChartVisualService(VisualService):
    obj: Visual


class AreaChartVisualService(VisualService):
    obj: Visual


class PieChartVisualService(VisualService):
    obj: Visual


class GaugeChartVisualService(VisualService):
    obj: Visual


class VisualConditionService(BaseDjangoModelService['VisualCondition']):
    obj: VisualCondition

    intelligence = VisualConditionIntelligenceService()
    processor = VisualConditionProcessorService()
    factory = VisualConditionFactoryService()
    transformation = VisualConditionTransformationService()
