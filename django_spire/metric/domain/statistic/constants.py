from __future__ import annotations

from django.db import models

STATISTIC_VALUE_COUNT_MAX = 100


class StatisticIntervalChoices(models.TextChoices):
    DAILY = 'daily', 'Daily'
    WEEKLY = 'weekly', 'Weekly'
    MONTHLY = 'monthly', 'Monthly'


class StatisticValueTypeChoices(models.TextChoices):
    CURRENCY = 'currency', 'Currency'
    PERCENTAGE = 'percentage', 'Percentage'
    NUMBER = 'number', 'Number'


PERCENTAGE_MOVING_WINDOW_DAYS = {
    StatisticIntervalChoices.DAILY: 2,
    StatisticIntervalChoices.WEEKLY: 7,
    StatisticIntervalChoices.MONTHLY: 30,
}


def percentage_moving_window_days(interval: str) -> int:
    return PERCENTAGE_MOVING_WINDOW_DAYS.get(interval, 7)
