from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction
from django.db.models import Max

from django_spire.contrib.constructor.service import BaseDjangoModelService

from django_spire.metric.visual.signage.services.factory_service import (
    SignageFactoryService,
    SignagePresentationFactoryService,
)
from django_spire.metric.visual.signage.services.intelligence_service import (
    SignageIntelligenceService,
    SignagePresentationIntelligenceService,
)
from django_spire.metric.visual.signage.services.processor_service import (
    SignagePresentationProcessorService,
    SignageProcessorService,
)
from django_spire.metric.visual.signage.services.transformation_service import (
    SignagePresentationTransformationService,
    SignageTransformationService,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.metric.visual.signage.models import Signage, SignagePresentation


class SignageService(BaseDjangoModelService['Signage']):
    obj: Signage

    intelligence = SignageIntelligenceService()
    processor = SignageProcessorService()
    factory = SignageFactoryService()
    transformation = SignageTransformationService()


class SignagePresentationService(BaseDjangoModelService['SignagePresentation']):
    obj: SignagePresentation

    intelligence = SignagePresentationIntelligenceService()
    processor = SignagePresentationProcessorService()
    factory = SignagePresentationFactoryService()
    transformation = SignagePresentationTransformationService()

    def save_model_obj(self, **field_data: dict | None) -> tuple[SignagePresentation, bool]:
        if self.obj.pk is None and self.obj.signage_id:
            with transaction.atomic():
                locked_signage = self._locked_signage()
                field_data = self._next_available_order(
                    locked_signage.signage_presentations, field_data
                )

                return super().save_model_obj(**field_data)

        return super().save_model_obj(**field_data)

    def _locked_signage(self) -> Signage:
        from django_spire.metric.visual.signage.models import Signage  # noqa: PLC0415

        return Signage.objects.select_for_update().get(pk=self.obj.signage_id)

    def _next_available_order(
        self, related: QuerySet[SignagePresentation], field_data: dict | None
    ) -> dict:
        order = field_data.get('order', self.obj.order) or 0

        if not related.filter(order=order).exists():
            field_data['order'] = order
            return field_data

        max_order = related.aggregate(max_order=Max('order'))['max_order']
        field_data['order'] = (max_order + 1) if max_order is not None else 0
        return field_data
