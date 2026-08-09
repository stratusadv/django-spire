from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.metric.visual.presentation.models import Presentation, Slide, SlideSection


class PresentationIntelligenceService(BaseDjangoModelService['Presentation']):
    obj: Presentation


class SlideIntelligenceService(BaseDjangoModelService['Slide']):
    obj: Slide


class SlideSectionIntelligenceService(BaseDjangoModelService['SlideSection']):
    obj: SlideSection
