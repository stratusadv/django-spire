from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.db.models import F
from django.utils import timezone

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from datetime import date

    from django_spire.metric.domain.statistic.models import (
        Statistic,
        StatisticGroup,
        StatisticValue,
    )


class StatisticGroupProcessorService(BaseDjangoModelService['StatisticGroup']):
    obj: StatisticGroup


class StatisticProcessorService(BaseDjangoModelService['Statistic']):
    obj: Statistic

    def add_value(
        self, reference: str, value: Decimal = Decimal(1), value_date: date | None = None
    ) -> StatisticValue:
        value_date = value_date or timezone.localdate()

        statistic_value, was_created = self.obj.values.get_or_create(
            reference=reference, date=value_date, defaults={'value': value}
        )

        if not was_created:
            self.obj.values.filter(pk=statistic_value.pk).update(value=F('value') + value)
            statistic_value.refresh_from_db()

        return statistic_value

    def subtract_value(
        self, reference: str, value: Decimal = Decimal(1), value_date: date | None = None
    ) -> StatisticValue:
        return self.add_value(reference, -value, value_date)

    def increment(self, reference: str, value_date: date | None = None) -> StatisticValue:
        return self.add_value(reference, Decimal(1), value_date)

    def decrement(self, reference: str, value_date: date | None = None) -> StatisticValue:
        return self.add_value(reference, Decimal(-1), value_date)


class StatisticValueProcessorService(BaseDjangoModelService['StatisticValue']):
    obj: StatisticValue
