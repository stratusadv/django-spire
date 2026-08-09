from __future__ import annotations

from typing import TYPE_CHECKING

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
