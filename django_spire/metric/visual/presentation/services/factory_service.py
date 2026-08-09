from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.metric.visual.presentation.models import Presentation, Slide, SlideSection


class PresentationFactoryService(BaseDjangoModelService['Presentation']):
    obj: Presentation


class SlideFactoryService(BaseDjangoModelService['Slide']):
    obj: Slide


class SlideSectionFactoryService(BaseDjangoModelService['SlideSection']):
    obj: SlideSection
