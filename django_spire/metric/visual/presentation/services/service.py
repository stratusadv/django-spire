from __future__ import annotations

from typing import TYPE_CHECKING

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


class SlideSectionService(BaseDjangoModelService['SlideSection']):
    obj: SlideSection

    intelligence = SlideSectionIntelligenceService()
    processor = SlideSectionProcessorService()
    factory = SlideSectionFactoryService()
    transformation = SlideSectionTransformationService()
