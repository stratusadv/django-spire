from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

from django_spire.metric.visual.presentation.constants import SLIDE_GRID_COLUMNS

if TYPE_CHECKING:
    from collections.abc import Iterable

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
        return self.obj.sections.filter(is_deleted=False, visual__is_deleted=False)


class SlideSectionTransformationService(BaseDjangoModelService['SlideSection']):
    obj: SlideSection

    @staticmethod
    def section_grid_styles(sections: Iterable[SlideSection]) -> dict[int, str]:
        ordered = sorted(sections, key=lambda section: (section.row, section.col, section.pk))

        row_counts: dict[int, int] = {}
        for section in ordered:
            row_counts[section.row] = row_counts.get(section.row, 0) + 1

        styles: dict[int, str] = {}
        positions: dict[int, int] = {}
        for section in ordered:
            count = row_counts[section.row]
            span = SLIDE_GRID_COLUMNS // count
            position = positions.get(section.row, 0)
            positions[section.row] = position + 1
            start = (position * span) + 1
            styles[section.pk] = f'grid-column: {start} / span {span}; grid-row: {section.row + 1};'

        return styles

    def render_context(self) -> dict:
        if not self.obj.visual_id or self.obj.visual.is_deleted:
            return {'visual': None, 'current_value': None, 'current_condition': None, 'chart': None}

        visual = self.obj.visual
        current_value = visual.services.transformation.current_value()
        period_start, period_end = visual.services.transformation.date_range()

        return {
            'visual': visual,
            'current_value': current_value,
            'current_condition': visual.services.transformation.current_condition(
                value=current_value
            ),
            'chart': visual.services.transformation.chart(),
            'period_start': period_start,
            'period_end': period_end,
        }
