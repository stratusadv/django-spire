from __future__ import annotations

from django.db.models import QuerySet, Q

from django_spire.contrib.queryset.mixins import SearchQuerySetMixin, SessionFilterQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet


class TaskQuerySet(
    HistoryQuerySet,
    SessionFilterQuerySetMixin,
    SearchQuerySetMixin,
):
    def complete(self) -> QuerySet:
        return self.filter(is_complete=True)

    def _session_filter(self, data: dict) -> QuerySet["TaskQuerySet"]:
        queryset = self

        # Todo: Move this into a tools file in queryset.
        lookup_map = {
            'name': 'name__icontains',
            'status': 'status',
        }

        lookup_kwargs = {
            lookup_map[k]: v
            for k, v in data.items()
            if k in lookup_map and v not in (None, "")
        }

        if search_term := data.get("search"):
            queryset = queryset.search(search_term)

        return queryset.filter(**lookup_kwargs)

    def search(self, value: str | None) -> QuerySet:
        if value is None:
            return self

        return self.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
