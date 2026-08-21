from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.utils import timezone

from django_spire.contrib.constructor.service import BaseDjangoModelService
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
        queryset = self.obj.values.select_related('sub_domain')
        if sub_domain is not None:
            queryset = queryset.for_sub_domain(sub_domain)
        return queryset

    def values_for_date(
        self, value_date: date_type | None = None, *, sub_domain: SubDomain | None = None
    ) -> QuerySet[StatisticValue]:
        value_date = value_date or timezone.localdate()
        return self.value_queryset(sub_domain).for_date(value_date).order_by('timestamp')

    def total_for_date(
        self, value_date: date_type | None = None, *, sub_domain: SubDomain | None = None
    ) -> Decimal:
        return self.values_for_date(value_date, sub_domain=sub_domain).total()

    def daily_summary(
        self, start_date: date_type, end_date: date_type, *, sub_domain: SubDomain | None = None
    ) -> dict[date_type, Decimal]:
        summary: dict[date_type, Decimal] = {}

        for value in (
            self.value_queryset(sub_domain).date_range(start_date, end_date).order_by('timestamp')
        ):
            day = timezone.localtime(value.timestamp).date()
            summary[day] = summary.get(day, Decimal(0)) + value.value

        return dict(sorted(summary.items()))

    def total_between(
        self, start_date: date_type, end_date: date_type, *, sub_domain: SubDomain | None = None
    ) -> Decimal:
        return self.value_queryset(sub_domain).date_range(start_date, end_date).total()

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
        return self.values_for_interval(value_date, sub_domain=sub_domain).total()

    def interval_summary(
        self, start_date: date_type, end_date: date_type, *, sub_domain: SubDomain | None = None
    ) -> dict[date_type, Decimal]:
        summary: dict[date_type, Decimal] = {}

        for value in self.value_queryset(sub_domain).date_range(start_date, end_date):
            day = timezone.localtime(value.timestamp).date()
            bucket_start, _ = interval_range(self.obj.interval, day)
            summary[bucket_start] = summary.get(bucket_start, Decimal(0)) + value.value

        return dict(sorted(summary.items()))


class StatisticValueTransformationService(BaseDjangoModelService['StatisticValue']):
    obj: StatisticValue
