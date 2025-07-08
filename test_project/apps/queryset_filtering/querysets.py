from __future__ import annotations

from django.db.models import QuerySet, Q

from django_spire.contrib.queryset.mixins import SearchQuerySetMixin, SessionQuerySetFilterMixin
from django_spire.history.querysets import HistoryQuerySet


class TaskQuerySet(
    HistoryQuerySet,
    SessionQuerySetFilterMixin,
    SearchQuerySetMixin,
):
    def complete(self) -> QuerySet:
        return self.filter(is_complete=True)

    def _session_filter(self, filter_data: dict) -> QuerySet['TaskQuerySet']:
        # Todo: Can I make this easier?
        query = Q()

        name = filter_data.get('name')
        if name:
            query &= Q(name__icontains=name)

        status = filter_data.get('status')
        if status:
            query &= Q(status=status)

        return self.filter(query)

    def search(self, value: str | None) -> QuerySet:
        if value is None:
            return self

        return self.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
