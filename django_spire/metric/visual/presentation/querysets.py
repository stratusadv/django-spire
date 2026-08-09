from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count

from django_spire.core.querysets import SearchQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.metric.visual.presentation.models import Presentation, Slide


class PresentationQuerySet(HistoryQuerySet, SearchQuerySetMixin):
    def bulk_filter(self, filter_data: dict) -> QuerySet[Presentation]:
        queryset = self

        search = filter_data.get('search', '')
        if search:
            queryset = queryset.search(search)

        return queryset

    def with_slides(self) -> QuerySet[Presentation]:
        return self.prefetch_related('slides', 'slides__sections', 'slides__sections__visual')

    def with_slide_count(self) -> QuerySet[Presentation]:
        return self.annotate(slide_count=Count('slide', distinct=True))


class SlideQuerySet(HistoryQuerySet):
    def for_presentation(self, presentation: Presentation) -> QuerySet:
        return self.filter(presentation=presentation)

    def with_sections(self) -> QuerySet:
        return self.prefetch_related('sections', 'sections__visual')


class SlideSectionQuerySet(HistoryQuerySet):
    def for_slide(self, slide: Slide) -> QuerySet:
        return self.filter(slide=slide)

    def with_visual(self) -> QuerySet:
        return self.select_related('visual')
