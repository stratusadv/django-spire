from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

from django_spire.metric.visual.presentation.models import Presentation
from django_spire.metric.visual.presentation.services.transformation_service import (
    SlideSectionTransformationService,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.metric.visual.signage.models import Signage, SignagePresentation


class SignageTransformationService(BaseDjangoModelService['Signage']):
    obj: Signage

    @property
    def display_title(self) -> str:
        if self.obj.title:
            return self.obj.title

        return self.obj.name

    def presentation_links(self) -> QuerySet[SignagePresentation]:
        return (
            self.obj.signage_presentations.select_related('presentation')
            .filter(is_deleted=False, presentation__is_deleted=False)
            .order_by('order')
        )

    def presentations(self) -> QuerySet[Presentation]:
        return (
            Presentation.objects.filter(
                presentation_link__signage=self.obj,
                presentation_link__is_deleted=False,
                presentation_link__presentation__is_deleted=False,
            )
            .order_by('presentation_link__order')
            .with_slides()
        )

    def display_slides(self) -> list[dict]:
        slides = []

        for link in self.presentation_links():
            presentation = link.presentation

            for slide in presentation.slides.filter(is_deleted=False).order_by('order'):
                section_sections = (
                    slide.sections.select_related('visual')
                    .prefetch_related('visual__conditions')
                    .filter(is_deleted=False, visual__is_deleted=False)
                )
                grid_styles = SlideSectionTransformationService.section_grid_styles(
                    section_sections
                )
                sections = [
                    {
                        'section': section,
                        'grid_style': grid_styles[section.pk],
                        **section.services.transformation.render_context(),
                    }
                    for section in section_sections.order_by('row', 'col')
                ]
                slides.append({'presentation': presentation, 'slide': slide, 'sections': sections})

        return slides


class SignagePresentationTransformationService(BaseDjangoModelService['SignagePresentation']):
    obj: SignagePresentation
