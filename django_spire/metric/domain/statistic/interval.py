from __future__ import annotations

from datetime import date, datetime, time, timedelta

from django.utils import timezone

from django_spire.metric.domain.statistic.constants import StatisticIntervalChoices


def local_day_start(value_date: date) -> datetime:
    return timezone.make_aware(datetime.combine(value_date, time.min))


def interval_range(interval: str, value_date: date) -> tuple[date, date]:
    if interval == StatisticIntervalChoices.WEEKLY:
        start = value_date - timedelta(days=(value_date.weekday() + 1) % 7)
        return start, start + timedelta(days=6)

    if interval == StatisticIntervalChoices.MONTHLY:
        start = value_date.replace(day=1)
        end = (start + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        return start, end

    return value_date, value_date
