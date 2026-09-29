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


def unit_end(interval: str, unit_start: date) -> date:
    if interval == StatisticIntervalChoices.WEEKLY:
        return unit_start + timedelta(days=6)

    if interval == StatisticIntervalChoices.MONTHLY:
        return (unit_start + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    return unit_start


def next_unit_start(interval: str, unit_start: date) -> date:
    if interval == StatisticIntervalChoices.WEEKLY:
        return unit_start + timedelta(days=7)

    if interval == StatisticIntervalChoices.MONTHLY:
        return (unit_start + timedelta(days=31)).replace(day=1)

    return unit_start + timedelta(days=1)


def display_window_range(interval: str, end_date: date, count: int) -> tuple[date, date]:
    if interval == StatisticIntervalChoices.WEEKLY:
        end_unit_start = end_date - timedelta(days=(end_date.weekday() + 1) % 7)
        start = end_unit_start - timedelta(weeks=count - 1)
        return start, start + timedelta(weeks=count) - timedelta(days=1)

    if interval == StatisticIntervalChoices.MONTHLY:
        months_back = end_date.year * 12 + end_date.month - count
        start_year, start_month = divmod(months_back, 12)
        start = date(start_year, start_month + 1, 1)
        end = unit_end(interval, date(end_date.year, end_date.month, 1))
        return start, end

    return end_date - timedelta(days=count - 1), end_date
