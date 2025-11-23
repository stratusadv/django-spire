from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Q

from django_spire.contrib.queryset.filter_tools import filter_by_lookup_map
from django_spire.contrib.queryset.mixins import SearchQuerySetMixin, SessionFilterQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from test_project.apps.infinite_scrolling.models import InfiniteScrolling


class InfiniteScrollingQuerySet(
    HistoryQuerySet,
    SessionFilterQuerySetMixin,
    SearchQuerySetMixin,
):
    def bulk_filter(self, filter_data: dict) -> QuerySet[InfiniteScrolling]:
        queryset = self

        filter_map = {
            'name': 'name__icontains',
        }

        search_term = filter_data.get('search')
        if search_term:
            queryset = queryset.search(search_term)

        return filter_by_lookup_map(queryset, filter_map, filter_data)

    def search(self, search_value: str | None) -> QuerySet[InfiniteScrolling]:
        if not search_value:
            return self

        search_value = search_value.strip()

        return self.filter(
            Q(name__icontains=search_value) |
            Q(description__icontains=search_value)
        )
