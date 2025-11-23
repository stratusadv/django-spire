from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Q

from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from test_project.apps.infinite_scrolling.models import InfiniteScrolling


class InfiniteScrollingQuerySet(HistoryQuerySet):
    def search(self, search_value: str) -> QuerySet[InfiniteScrolling]:
        return self.filter(
            Q(name__icontains=search_value) |
            Q(description__icontains=search_value)
        )
