from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Max

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
    from django.db.models import QuerySet

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

    def save_model_obj(self, **field_data: dict | None) -> tuple[VisualCondition, bool]:
        if self.obj.pk is None and self.obj.visual_id:
            field_data = self._next_available_order(self.obj.visual.conditions, field_data)

        return super().save_model_obj(**field_data)

    def _next_available_order(
        self, related: QuerySet[VisualCondition], field_data: dict | None
    ) -> dict:
        order = field_data.get('order', self.obj.order) or 0

        if not related.filter(order=order).exists():
            field_data['order'] = order
            return field_data

        max_order = related.aggregate(max_order=Max('order'))['max_order']
        field_data['order'] = (max_order + 1) if max_order is not None else 0
        return field_data


class VisualReferenceService(BaseDjangoModelService['VisualReference']):
    obj: VisualReference

    def save_model_obj(self, **field_data: dict | None) -> tuple[VisualReference, bool]:
        if self.obj.pk is None and self.obj.visual_id:
            field_data = self._next_available_order(self.obj.visual.references, field_data)

        return super().save_model_obj(**field_data)

    def _next_available_order(
        self, related: QuerySet[VisualReference], field_data: dict | None
    ) -> dict:
        order = field_data.get('order', self.obj.order) or 0

        if not related.filter(order=order).exists():
            field_data['order'] = order
            return field_data

        max_order = related.aggregate(max_order=Max('order'))['max_order']
        field_data['order'] = (max_order + 1) if max_order is not None else 0
        return field_data


class VisualRegionService(BaseDjangoModelService['VisualRegion']):
    obj: VisualRegion

    intelligence = VisualRegionIntelligenceService()
    processor = VisualRegionProcessorService()
    factory = VisualRegionFactoryService()
    transformation = VisualRegionTransformationService()
