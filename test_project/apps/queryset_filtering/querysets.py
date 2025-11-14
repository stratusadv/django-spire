from __future__ import annotations

from django.db.models import QuerySet, Q

from django_spire.contrib.queryset.filter_tools import filter_by_lookup_map
from django_spire.contrib.queryset.mixins import SearchQuerySetMixin, SessionFilterQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet


class TaskQuerySet(
    HistoryQuerySet,
    SessionFilterQuerySetMixin,
    SearchQuerySetMixin,
):
    def complete(self) -> QuerySet:
        return self.filter(is_complete=True)

    def prefetch_users(self):
        return self.prefetch_related('users__user')

    def bulk_filter(self, filter_data: dict) -> QuerySet[TaskQuerySet]:
        queryset = self

        filter_map = {
            'name': 'name__icontains',
            'status': 'status',
            'users': 'user__user__id__in'
        }

        search_term = filter_data.get('search')
        if search_term:
            queryset = queryset.search(search_term)

        return filter_by_lookup_map(queryset, filter_map, filter_data)

    def search(self, search_value: str | None) -> QuerySet:
        if not search_value:
            return self

        search_value = search_value.strip()

        return self.filter(
            Q(name__icontains=search_value) |
            Q(description__icontains=search_value)
        )
