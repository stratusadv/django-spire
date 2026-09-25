from __future__ import annotations

from django_spire.metric.domain.statistic.constants import StatisticIntervalChoices

VISUAL_REGION_LIVE_UPDATE_INTERVAL = 10

DISPLAY_UNIT_COUNT_MIN = 1
DISPLAY_UNIT_COUNT_MAX = 104
DEFAULT_DISPLAY_UNIT_COUNT = 8
DEFAULT_DISPLAY_UNIT_COUNTS = {
    StatisticIntervalChoices.DAILY: 8,
    StatisticIntervalChoices.WEEKLY: 12,
    StatisticIntervalChoices.MONTHLY: 13,
}
DISPLAY_UNIT_LABELS = {
    StatisticIntervalChoices.DAILY: 'day(s)',
    StatisticIntervalChoices.WEEKLY: 'week(s)',
    StatisticIntervalChoices.MONTHLY: 'month(s)',
}


def effective_display_unit_count(interval: str | None, display_unit_count: int | None) -> int:
    if display_unit_count:
        return display_unit_count

    return DEFAULT_DISPLAY_UNIT_COUNTS.get(interval, DEFAULT_DISPLAY_UNIT_COUNT)
