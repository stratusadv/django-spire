from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

from django_spire.metric.visual.presentation.services.factory_service import PresentationFactoryService
from django_spire.metric.visual.presentation.services.intelligence_service import PresentationIntelligenceService
from django_spire.metric.visual.presentation.services.processor_service import PresentationProcessorService
from django_spire.metric.visual.presentation.services.transformation_service import PresentationTransformationService

if TYPE_CHECKING:
    from django_spire.metric.visual.presentation.models import Presentation


class PresentationService(BaseDjangoModelService['Presentation']):
    obj: Presentation

    intelligence = PresentationIntelligenceService()
    processor = PresentationProcessorService()
    factory = PresentationFactoryService()
    transformation = PresentationTransformationService()
