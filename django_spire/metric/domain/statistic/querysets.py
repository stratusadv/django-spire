from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import QuerySet, Sum

from django_spire.core.querysets import SearchQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

    from django_spire.metric.domain.statistic.models import (
        Statistic,
        StatisticGroup,
        StatisticValue,
    )


class StatisticGroupQuerySet(HistoryQuerySet, SearchQuerySetMixin):
    def bulk_filter(self, filter_data: dict) -> QuerySet[StatisticGroup]:
        queryset = self

        search = filter_data.get('search', '')
        if search:
            queryset = queryset.search(search)

        return queryset


class StatisticQuerySet(HistoryQuerySet, SearchQuerySetMixin):
    def bulk_filter(self, filter_data: dict) -> QuerySet[Statistic]:
        queryset = self

        search = filter_data.get('search', '')
        if search:
            queryset = queryset.search(search)

        return queryset


class StatisticValueQuerySet(QuerySet):
    def for_date(self, value_date: date) -> QuerySet[StatisticValue]:
        return self.filter(date=value_date)

    def date_range(self, start_date: date, end_date: date) -> QuerySet[StatisticValue]:
        return self.filter(date__gte=start_date, date__lte=end_date)

    def for_reference(self, reference: str) -> QuerySet[StatisticValue]:
        return self.filter(reference=reference)

    def total(self) -> Decimal:
        return self.aggregate(total=Sum('value'))['total'] or 0
