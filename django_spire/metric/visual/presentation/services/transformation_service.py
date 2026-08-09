from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.metric.visual.presentation.models import Presentation, Slide, SlideSection


class PresentationTransformationService(BaseDjangoModelService['Presentation']):
    obj: Presentation

    def slides(self) -> QuerySet[Slide]:
        return self.obj.slides.with_sections().filter(is_deleted=False)

    def slide_count(self) -> int:
        return self.obj.slides.filter(is_deleted=False).count()


class SlideTransformationService(BaseDjangoModelService['Slide']):
    obj: Slide

    def sections(self) -> QuerySet[SlideSection]:
        return self.obj.sections.select_related('visual').filter(is_deleted=False)


class SlideSectionTransformationService(BaseDjangoModelService['SlideSection']):
    obj: SlideSection

    def render_context(self) -> dict:
        if not self.obj.visual_id:
            return {'visual': None, 'current_value': None, 'current_condition': None, 'chart': None}

        visual = self.obj.visual

        return {
            'visual': visual,
            'current_value': visual.services.transformation.current_value(),
            'current_condition': visual.services.transformation.current_condition(),
            'chart': visual.services.transformation.chart(),
        }
