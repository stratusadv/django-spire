from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Sum
from django.utils import timezone

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from datetime import date as date_type
    from decimal import Decimal

    from django.db.models import QuerySet

    from django_spire.metric.domain.statistic.models import (
        Statistic,
        StatisticGroup,
        StatisticValue,
    )


class StatisticGroupTransformationService(BaseDjangoModelService['StatisticGroup']):
    obj: StatisticGroup


class StatisticTransformationService(BaseDjangoModelService['Statistic']):
    obj: Statistic

    def values_for_date(self, value_date: date_type | None = None) -> QuerySet[StatisticValue]:
        value_date = value_date or timezone.localdate()
        return self.obj.values.for_date(value_date)

    def total_for_date(self, value_date: date_type | None = None) -> Decimal:
        return self.values_for_date(value_date).total()

    def daily_summary(self, start_date: date_type, end_date: date_type) -> dict[date_type, Decimal]:
        rows = (
            self.obj.values.date_range(start_date, end_date)
            .values('date')
            .annotate(total=Sum('value'))
            .order_by('date')
        )

        return {row['date']: row['total'] for row in rows}

    def total_between(self, start_date: date_type, end_date: date_type) -> Decimal:
        return self.obj.values.date_range(start_date, end_date).total()


class StatisticValueTransformationService(BaseDjangoModelService['StatisticValue']):
    obj: StatisticValue
