from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.core.querysets import SearchQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

from django_spire.metric.visual.choices import VisualKindChoices

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.metric.visual.models import Visual, VisualReference


class VisualQuerySet(HistoryQuerySet, SearchQuerySetMixin):
    def bulk_filter(self, filter_data: dict) -> QuerySet[Visual]:
        queryset = self

        search = filter_data.get('search', '')
        if search:
            queryset = queryset.search(search)

        return queryset

    def with_statistic(self) -> QuerySet[Visual]:
        return self.select_related('statistic')

    def with_conditions(self) -> QuerySet[Visual]:
        return self.prefetch_related('conditions')

    def with_references(self) -> QuerySet[Visual]:
        return self.prefetch_related('references')

    def of_kind(self, kind: str) -> QuerySet[Visual]:
        return self.filter(kind=kind)

    def indicators(self) -> QuerySet[Visual]:
        return self.of_kind(VisualKindChoices.INDICATOR)

    def charts(self) -> QuerySet[Visual]:
        return self.exclude(kind=VisualKindChoices.INDICATOR)


class VisualConditionQuerySet(HistoryQuerySet):
    def for_visual(self, visual: Visual) -> QuerySet:
        return self.filter(visual=visual)


class VisualReferenceQuerySet(HistoryQuerySet):
    def for_visual(self, visual: Visual) -> QuerySet[VisualReference]:
        return self.filter(visual=visual)
