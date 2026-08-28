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
