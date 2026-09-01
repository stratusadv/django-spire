from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.utils import timezone
from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncDate

from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_spire.metric.domain.statistic.constants import (
    StatisticValueTypeChoices,
    percentage_moving_window_days,
)
from django_spire.metric.domain.statistic.interval import interval_range

if TYPE_CHECKING:
    from datetime import date as date_type

    from django.db.models import QuerySet

    from django_spire.metric.domain.models import SubDomain

    from django_spire.metric.domain.statistic.models import (
        Statistic,
        StatisticGroup,
        StatisticValue,
    )


class StatisticGroupTransformationService(BaseDjangoModelService['StatisticGroup']):
    obj: StatisticGroup


class StatisticTransformationService(BaseDjangoModelService['Statistic']):
    obj: Statistic

    def value_queryset(self, sub_domain: SubDomain | None = None) -> QuerySet[StatisticValue]:
        if self.obj.is_deleted:
            return self.obj.values.none()

        queryset = self.obj.values.select_related('sub_domain')
        if sub_domain is not None:
            queryset = queryset.for_sub_domain(sub_domain)
        return queryset

    def aggregate(self, queryset: QuerySet[StatisticValue]) -> Decimal:
        if self.obj.value_type == StatisticValueTypeChoices.PERCENTAGE:
            return queryset.average()

        return queryset.total()

    def values_for_date(
        self, value_date: date_type | None = None, *, sub_domain: SubDomain | None = None
    ) -> QuerySet[StatisticValue]:
        value_date = value_date or timezone.localdate()
        return self.value_queryset(sub_domain).for_date(value_date).order_by('timestamp')

    def total_for_date(
        self, value_date: date_type | None = None, *, sub_domain: SubDomain | None = None
    ) -> Decimal:
        return self.aggregate(self.values_for_date(value_date, sub_domain=sub_domain))

    def daily_summary(
        self, start_date: date_type, end_date: date_type, *, sub_domain: SubDomain | None = None
    ) -> dict[date_type, Decimal]:
        aggregate = Avg if self.obj.value_type == StatisticValueTypeChoices.PERCENTAGE else Sum

        rows = (
            self.value_queryset(sub_domain)
            .date_range(start_date, end_date)
            .annotate(day=TruncDate('timestamp', tzinfo=timezone.get_current_timezone()))
            .values('day')
            .annotate(total=aggregate('value'))
            .order_by('day')
        )

        return {row['day']: row['total'] for row in rows}

    def total_between(
        self, start_date: date_type, end_date: date_type, *, sub_domain: SubDomain | None = None
    ) -> Decimal:
        queryset = self.value_queryset(sub_domain).date_range(start_date, end_date)
        return self.aggregate(queryset)

    def interval_bounds(self, value_date: date_type | None = None) -> tuple[date_type, date_type]:
        value_date = value_date or timezone.localdate()
        return interval_range(self.obj.interval, value_date)

    def values_for_interval(
        self, value_date: date_type | None = None, *, sub_domain: SubDomain | None = None
    ) -> QuerySet[StatisticValue]:
        start_date, end_date = self.interval_bounds(value_date)
        return (
            self.value_queryset(sub_domain).date_range(start_date, end_date).order_by('timestamp')
        )

    def total_for_interval(
        self, value_date: date_type | None = None, *, sub_domain: SubDomain | None = None
    ) -> Decimal:
        if self.obj.value_type == StatisticValueTypeChoices.PERCENTAGE:
            value_date = value_date or timezone.localdate()
            window_days = percentage_moving_window_days(self.obj.interval)
            return self.value_queryset(sub_domain).moving_window_average(value_date, window_days)

        return self.values_for_interval(value_date, sub_domain=sub_domain).total()

    def interval_summary(
        self, start_date: date_type, end_date: date_type, *, sub_domain: SubDomain | None = None
    ) -> dict[date_type, Decimal]:
        is_percentage = self.obj.value_type == StatisticValueTypeChoices.PERCENTAGE

        queryset = (
            self.value_queryset(sub_domain)
            .date_range(start_date, end_date)
            .annotate(day=TruncDate('timestamp', tzinfo=timezone.get_current_timezone()))
            .values('day')
            .annotate(total=Sum('value'))
        )
        if is_percentage:
            queryset = queryset.annotate(count=Count('pk'))

        totals: dict[date_type, Decimal] = {}
        counts: dict[date_type, int] = {}
        for row in queryset:
            bucket_start, _ = interval_range(self.obj.interval, row['day'])
            totals[bucket_start] = totals.get(bucket_start, Decimal(0)) + row['total']
            if is_percentage:
                counts[bucket_start] = counts.get(bucket_start, 0) + row['count']

        if is_percentage:
            return dict(sorted((start, totals[start] / counts[start]) for start in totals))

        return dict(sorted(totals.items()))


class StatisticValueTransformationService(BaseDjangoModelService['StatisticValue']):
    obj: StatisticValue
