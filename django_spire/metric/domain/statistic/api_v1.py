from __future__ import annotations

from datetime import date as date_type
from decimal import Decimal

from ninja import Router
from pydantic import BaseModel, Field

from django_spire.metric.domain.statistic import models

router = Router()


class StatisticValueIn(BaseModel):
    reference: str = Field(..., min_length=1)
    value: Decimal = Decimal(1)
    value_date: date_type | None = None


class StatisticValueOut(BaseModel):
    statistic_id: int
    reference: str
    date: date_type
    value: Decimal


@router.post('{statistic_id}/record')
def record_value(request, statistic_id: int, payload: StatisticValueIn) -> StatisticValueOut:
    statistic = models.Statistic.objects.get(pk=statistic_id)
    statistic_value = statistic.services.processor.add_value(
        reference=payload.reference, value=payload.value, value_date=payload.value_date
    )
    return StatisticValueOut(
        statistic_id=statistic.id,
        reference=statistic_value.reference,
        date=statistic_value.date,
        value=statistic_value.value,
    )


@router.get('{statistic_id}/total')
def total_for_date(request, statistic_id: int, value_date: date_type | None = None) -> dict:
    statistic = models.Statistic.objects.get(pk=statistic_id)
    return {
        'date': value_date.isoformat() if value_date else None,
        'total': str(statistic.services.transformation.total_for_date(value_date)),
    }


@router.get('{statistic_id}/summary')
def daily_summary(request, statistic_id: int, start_date: date_type, end_date: date_type) -> dict:
    statistic = models.Statistic.objects.get(pk=statistic_id)
    summary = statistic.services.transformation.daily_summary(start_date, end_date)
    return {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'totals': {k.isoformat(): str(v) for k, v in summary.items()},
    }


@router.get('{statistic_id}/values')
def values_for_date(
    request, statistic_id: int, value_date: date_type | None = None
) -> list[StatisticValueOut]:
    statistic = models.Statistic.objects.get(pk=statistic_id)
    values = statistic.services.transformation.values_for_date(value_date)
    return [
        StatisticValueOut(
            statistic_id=sv.statistic_id, reference=sv.reference, date=sv.date, value=sv.value
        )
        for sv in values
    ]
