from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db.models import Avg, QuerySet, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from django_spire.core.querysets import SearchQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet
from django_spire.metric.domain.statistic.interval import local_day_start

if TYPE_CHECKING:
    from uuid import UUID

    from django_spire.metric.domain.models import SubDomain

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
    def for_key(self, key: str | UUID) -> QuerySet[Statistic]:
        return self.filter(key=key)

    def bulk_filter(self, filter_data: dict) -> QuerySet[Statistic]:
        queryset = self

        search = filter_data.get('search', '')
        if search:
            queryset = queryset.search(search)

        return queryset


class StatisticValueQuerySet(QuerySet):
    def for_date(self, value_date: date) -> QuerySet[StatisticValue]:
        return self.filter(
            timestamp__gte=local_day_start(value_date),
            timestamp__lt=local_day_start(value_date + timedelta(days=1)),
        )

    def date_range(self, start_date: date, end_date: date) -> QuerySet[StatisticValue]:
        return self.filter(
            timestamp__gte=local_day_start(start_date),
            timestamp__lt=local_day_start(end_date + timedelta(days=1)),
        )

    def for_reference(self, reference: str) -> QuerySet[StatisticValue]:
        return self.filter(reference=reference)

    def for_sub_domain(self, sub_domain: SubDomain) -> QuerySet[StatisticValue]:
        return self.filter(sub_domain=sub_domain)

    def total(self) -> Decimal:
        return self.aggregate(total=Sum('value'))['total'] or Decimal(0)

    def average(self) -> Decimal:
        return self.aggregate(total=Avg('value'))['total'] or Decimal(0)

    def daily_averages(self, start_date: date, end_date: date) -> list[tuple[date, Decimal]]:
        rows = (
            self.date_range(start_date, end_date)
            .annotate(day=TruncDate('timestamp', tzinfo=timezone.get_current_timezone()))
            .values('day')
            .annotate(total=Avg('value'))
            .order_by('day')
        )

        return [(row['day'], Decimal(row['total'])) for row in rows]

    def moving_window_average(self, end_date: date, window_days: int) -> Decimal:
        start_date = end_date - timedelta(days=window_days - 1)

        rows = (
            self.date_range(start_date, end_date)
            .annotate(day=TruncDate('timestamp', tzinfo=timezone.get_current_timezone()))
            .values('day')
            .annotate(total=Avg('value'))
        )

        values = [row['total'] for row in rows]
        if not values:
            return Decimal(0)

        return sum(values, Decimal(0)) / len(values)
