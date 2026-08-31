from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

from django_spire.metric.visual.services.factory_service import (
    VisualConditionFactoryService,
    VisualFactoryService,
    VisualRegionFactoryService,
)
from django_spire.metric.visual.services.intelligence_service import (
    VisualConditionIntelligenceService,
    VisualIntelligenceService,
    VisualRegionIntelligenceService,
)
from django_spire.metric.visual.services.processor_service import (
    VisualConditionProcessorService,
    VisualProcessorService,
    VisualRegionProcessorService,
)
from django_spire.metric.visual.services.transformation_service import (
    VisualConditionTransformationService,
    VisualRegionTransformationService,
    VisualTransformationService,
)

if TYPE_CHECKING:
    from django_spire.metric.visual.models import (
        Visual,
        VisualCondition,
        VisualReference,
        VisualRegion,
    )


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


class VisualReferenceService(BaseDjangoModelService['VisualReference']):
    obj: VisualReference


class VisualRegionService(BaseDjangoModelService['VisualRegion']):
    obj: VisualRegion

    intelligence = VisualRegionIntelligenceService()
    processor = VisualRegionProcessorService()
    factory = VisualRegionFactoryService()
    transformation = VisualRegionTransformationService()
