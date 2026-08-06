from __future__ import annotations

from django.db import models

LIST_FILTERING_SESSION_KEY = 'statistic_list_filter'


class StatisticIntervalChoices(models.TextChoices):
    DAILY = 'daily', 'Daily'
    WEEKLY = 'weekly', 'Weekly'
    MONTHLY = 'monthly', 'Monthly'
