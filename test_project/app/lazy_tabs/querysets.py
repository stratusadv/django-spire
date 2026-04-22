from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Q

from django_spire.contrib.queryset.mixins import SearchQuerySetMixin, SessionFilterQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from test_project.apps.lazy_tabs.models import LazyTabs


class LazyTabsQuerySet(
    HistoryQuerySet,
    SessionFilterQuerySetMixin,
    SearchQuerySetMixin,
):
    def search(self, search_value: str | None) -> QuerySet[LazyTabs]:
        if not search_value:
            return self

        search_value = search_value.strip()

        return self.filter(
            Q(name__icontains=search_value) |
            Q(description__icontains=search_value)
        )
