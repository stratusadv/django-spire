from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.utils import timezone

from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_spire.contrib.constructor.service.exceptions import ServiceError

if TYPE_CHECKING:
    from datetime import datetime

    from django_spire.metric.domain.models import SubDomain

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
        self,
        reference: str,
        sub_domain: SubDomain,
        value: float | str | Decimal = 1,
        *,
        value_timestamp: datetime | None = None,
    ) -> StatisticValue:
        if sub_domain.domain_id != self.obj.group.domain_id:
            message = (
                f"Sub-domain '{sub_domain}' does not belong to domain '{self.obj.group.domain}'"
            )
            raise ServiceError(message)

        value = Decimal(value)
        stamp = value_timestamp or timezone.now()
        if timezone.is_naive(stamp):
            stamp = timezone.make_aware(stamp)

        statistic_value = self.obj.values.create(
            sub_domain=sub_domain, reference=reference, timestamp=stamp, value=value
        )
        statistic_value.value = statistic_value.value.quantize(self._value_precision())

        return statistic_value

    def _value_precision(self) -> Decimal:
        decimal_places = self.obj.values.model._meta.get_field('value').decimal_places
        return Decimal(1).scaleb(-decimal_places)

    def subtract_value(
        self,
        reference: str,
        sub_domain: SubDomain,
        value: float | str | Decimal = 1,
        *,
        value_timestamp: datetime | None = None,
    ) -> StatisticValue:
        return self.add_value(
            reference, sub_domain, -Decimal(value), value_timestamp=value_timestamp
        )

    def increment(
        self, reference: str, sub_domain: SubDomain, *, value_timestamp: datetime | None = None
    ) -> StatisticValue:
        return self.add_value(reference, sub_domain, Decimal(1), value_timestamp=value_timestamp)

    def decrement(
        self, reference: str, sub_domain: SubDomain, *, value_timestamp: datetime | None = None
    ) -> StatisticValue:
        return self.add_value(reference, sub_domain, Decimal(-1), value_timestamp=value_timestamp)


class StatisticValueProcessorService(BaseDjangoModelService['StatisticValue']):
    obj: StatisticValue
