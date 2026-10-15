from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction
from django.db.models import Max

from django_spire.contrib.constructor.service import BaseDjangoModelService

from django_spire.metric.visual.presentation.services.factory_service import (
    PresentationFactoryService,
    SlideFactoryService,
    SlideSectionFactoryService,
)
from django_spire.metric.visual.presentation.services.intelligence_service import (
    PresentationIntelligenceService,
    SlideIntelligenceService,
    SlideSectionIntelligenceService,
)
from django_spire.metric.visual.presentation.services.processor_service import (
    PresentationProcessorService,
    SlideProcessorService,
    SlideSectionProcessorService,
)
from django_spire.metric.visual.presentation.services.transformation_service import (
    PresentationTransformationService,
    SlideSectionTransformationService,
    SlideTransformationService,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.metric.visual.presentation.models import Presentation, Slide, SlideSection


class PresentationService(BaseDjangoModelService['Presentation']):
    obj: Presentation

    intelligence = PresentationIntelligenceService()
    processor = PresentationProcessorService()
    factory = PresentationFactoryService()
    transformation = PresentationTransformationService()


class SlideService(BaseDjangoModelService['Slide']):
    obj: Slide

    intelligence = SlideIntelligenceService()
    processor = SlideProcessorService()
    factory = SlideFactoryService()
    transformation = SlideTransformationService()

    @classmethod
    def next_order(cls, related: QuerySet[Slide]) -> int:
        max_order = related.aggregate(max_order=Max('order'))['max_order']
        return (max_order + 1) if max_order is not None else 0

    def save_model_obj(self, **field_data: dict | None) -> tuple[Slide, bool]:
        if self.obj.pk is None and self.obj.presentation_id:
            with transaction.atomic():
                locked_presentation = self._locked_presentation()
                field_data = self._next_available_order(locked_presentation.slides, field_data)

                return super().save_model_obj(**field_data)

        return super().save_model_obj(**field_data)

    def _locked_presentation(self) -> Presentation:
        from django_spire.metric.visual.presentation.models import Presentation  # noqa: PLC0415

        return Presentation.objects.select_for_update().get(pk=self.obj.presentation_id)

    def _next_available_order(self, related: QuerySet[Slide], field_data: dict | None) -> dict:
        order = field_data.get('order', self.obj.order) or 0

        if not related.filter(order=order).exists():
            field_data['order'] = order
            return field_data

        field_data['order'] = self.next_order(related)
        return field_data


class SlideSectionService(BaseDjangoModelService['SlideSection']):
    obj: SlideSection

    intelligence = SlideSectionIntelligenceService()
    processor = SlideSectionProcessorService()
    factory = SlideSectionFactoryService()
    transformation = SlideSectionTransformationService()
