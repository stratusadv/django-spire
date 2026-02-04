from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Q

from django_spire.history.querysets import HistoryQuerySet
from django_spire.contrib.queryset.mixins import SearchQuerySetMixin, \
    SessionFilterQuerySetMixin

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.metric.domain.statistic.models import Statistic


class StatisticQuerySet(
    HistoryQuerySet,
    SearchQuerySetMixin,
    SessionFilterQuerySetMixin
):
    def bulk_filter(self, filter_data: dict) -> QuerySet[Statistic]:
        queryset = self

        search = filter_data.get('search', '')
        if search:
            queryset = queryset.search(search)

        return queryset
