from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction
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

    @classmethod
    def next_order(cls, related: QuerySet[VisualCondition]) -> int:
        max_order = related.aggregate(max_order=Max('order'))['max_order']
        return (max_order + 1) if max_order is not None else 0

    def save_model_obj(self, **field_data: dict | None) -> tuple[VisualCondition, bool]:
        if self.obj.pk is None and self.obj.visual_id:
            with transaction.atomic():
                locked_visual = self._locked_visual()
                field_data = self._next_available_order(locked_visual.conditions, field_data)

                return super().save_model_obj(**field_data)

        return super().save_model_obj(**field_data)

    def _locked_visual(self) -> Visual:
        from django_spire.metric.visual.models import Visual  # noqa: PLC0415

        return Visual.objects.select_for_update().get(pk=self.obj.visual_id)

    def _next_available_order(
        self, related: QuerySet[VisualCondition], field_data: dict | None
    ) -> dict:
        order = field_data.get('order', self.obj.order) or 0

        if not related.filter(order=order).exists():
            field_data['order'] = order
            return field_data

        field_data['order'] = self.next_order(related)
        return field_data


class VisualReferenceService(BaseDjangoModelService['VisualReference']):
    obj: VisualReference

    @classmethod
    def next_order(cls, related: QuerySet[VisualReference]) -> int:
        max_order = related.aggregate(max_order=Max('order'))['max_order']
        return (max_order + 1) if max_order is not None else 0

    def save_model_obj(self, **field_data: dict | None) -> tuple[VisualReference, bool]:
        if self.obj.pk is None and self.obj.visual_id:
            with transaction.atomic():
                locked_visual = self._locked_visual()
                field_data = self._next_available_order(locked_visual.references, field_data)

                return super().save_model_obj(**field_data)

        return super().save_model_obj(**field_data)

    def _locked_visual(self) -> Visual:
        from django_spire.metric.visual.models import Visual  # noqa: PLC0415

        return Visual.objects.select_for_update().get(pk=self.obj.visual_id)

    def _next_available_order(
        self, related: QuerySet[VisualReference], field_data: dict | None
    ) -> dict:
        order = field_data.get('order', self.obj.order) or 0

        if not related.filter(order=order).exists():
            field_data['order'] = order
            return field_data

        field_data['order'] = self.next_order(related)
        return field_data


class VisualRegionService(BaseDjangoModelService['VisualRegion']):
    obj: VisualRegion

    intelligence = VisualRegionIntelligenceService()
    processor = VisualRegionProcessorService()
    factory = VisualRegionFactoryService()
    transformation = VisualRegionTransformationService()
