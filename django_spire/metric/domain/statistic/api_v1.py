from __future__ import annotations

import uuid
from datetime import date as date_type  # noqa: TC003
from datetime import datetime as datetime_type  # noqa: TC003
from decimal import Decimal

from django.http import HttpRequest
from django.http import Http404
from ninja import Query, Router
from pydantic import BaseModel, Field

from django_spire.metric.domain.models import SubDomain
from django_spire.metric.domain.statistic import models

router = Router()


class StatisticValueIn(BaseModel):
    reference: str = Field(..., min_length=1, max_length=255)
    sub_domain_key: uuid.UUID
    value: Decimal = Decimal(1)


class StatisticValueOut(BaseModel):
    statistic_key: uuid.UUID
    reference: str
    sub_domain_key: uuid.UUID
    timestamp: datetime_type
    value: Decimal


def _get_statistic(statistic_key: str, active_required: bool = False) -> models.Statistic:
    try:
        key = uuid.UUID(str(statistic_key))
    except ValueError:
        raise Http404 from None

    queryset = models.Statistic.objects.for_key(key)
    if active_required:
        queryset = queryset.active().not_deleted()

    statistic = queryset.first()
    if statistic is None:
        raise Http404

    return statistic


def _get_sub_domain(
    statistic: models.Statistic, sub_domain_key: uuid.UUID | None, active_required: bool = False
) -> SubDomain | None:
    if sub_domain_key is None:
        return None

    queryset = SubDomain.objects.for_key(sub_domain_key).filter(domain=statistic.group.domain)
    if active_required:
        queryset = queryset.active().not_deleted()

    sub_domain = queryset.first()
    if sub_domain is None:
        raise Http404

    return sub_domain


@router.post('{statistic_key}/record')
def record_value(
    request: HttpRequest, statistic_key: str, payload: StatisticValueIn
) -> StatisticValueOut:
    statistic = _get_statistic(statistic_key, active_required=True)
    sub_domain = _get_sub_domain(statistic, payload.sub_domain_key, active_required=True)
    statistic_value = statistic.services.processor.add_value(
        reference=payload.reference, sub_domain=sub_domain, value=payload.value
    )
    return StatisticValueOut(
        statistic_key=statistic.key,
        reference=statistic_value.reference,
        sub_domain_key=statistic_value.sub_domain.key,
        timestamp=statistic_value.timestamp,
        value=statistic_value.value,
    )


@router.get('{statistic_key}/total')
def total_for_interval(
    request: HttpRequest,
    statistic_key: str,
    value_date: date_type | None = None,
    sub_domain_key: uuid.UUID | None = None,
) -> dict:
    statistic = _get_statistic(statistic_key)
    sub_domain = _get_sub_domain(statistic, sub_domain_key)
    start_date, end_date = statistic.services.transformation.interval_bounds(value_date)
    total = statistic.services.transformation.total_for_interval(value_date, sub_domain=sub_domain)
    return {
        'date': value_date.isoformat() if value_date else None,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'total': str(total),
    }


@router.get('{statistic_key}/summary')
def interval_summary(
    request: HttpRequest,
    statistic_key: str,
    start_date: date_type,
    end_date: date_type,
    sub_domain_key: uuid.UUID | None = None,
) -> dict:
    statistic = _get_statistic(statistic_key)
    sub_domain = _get_sub_domain(statistic, sub_domain_key)
    summary = statistic.services.transformation.interval_summary(
        start_date, end_date, sub_domain=sub_domain
    )
    return {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'totals': {k.isoformat(): str(v) for k, v in summary.items()},
    }


@router.get('{statistic_key}/values')
def values_for_interval(
    request: HttpRequest,
    statistic_key: str,
    value_date: date_type | None = None,
    sub_domain_key: uuid.UUID | None = None,
    limit: int = Query(1000, ge=1, le=5000),
    offset: int = Query(0, ge=0),
) -> list[StatisticValueOut]:
    statistic = _get_statistic(statistic_key)
    sub_domain = _get_sub_domain(statistic, sub_domain_key)
    values = statistic.services.transformation.values_for_interval(
        value_date, sub_domain=sub_domain
    )[offset : offset + limit]
    return [
        StatisticValueOut(
            statistic_key=statistic.key,
            reference=sv.reference,
            sub_domain_key=sv.sub_domain.key,
            timestamp=sv.timestamp,
            value=sv.value,
        )
        for sv in values
    ]
