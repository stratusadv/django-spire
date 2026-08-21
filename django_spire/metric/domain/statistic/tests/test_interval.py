from __future__ import annotations

from datetime import date, timedelta

from django.test import TestCase

from django_spire.metric.domain.statistic.constants import StatisticIntervalChoices
from django_spire.metric.domain.statistic.interval import interval_range, local_day_start


class IntervalRangeTestCase(TestCase):
    def test_daily_range_is_single_day(self):
        value_date = date(2026, 8, 19)
        assert interval_range(StatisticIntervalChoices.DAILY, value_date) == (
            value_date,
            value_date,
        )

    def test_weekly_range_midweek(self):
        wednesday = date(2026, 8, 19)
        assert interval_range(StatisticIntervalChoices.WEEKLY, wednesday) == (
            date(2026, 8, 16),
            date(2026, 8, 22),
        )

    def test_weekly_range_from_sunday(self):
        sunday = date(2026, 8, 16)
        assert interval_range(StatisticIntervalChoices.WEEKLY, sunday) == (
            sunday,
            date(2026, 8, 22),
        )

    def test_weekly_range_from_saturday(self):
        saturday = date(2026, 8, 22)
        assert interval_range(StatisticIntervalChoices.WEEKLY, saturday) == (
            date(2026, 8, 16),
            saturday,
        )

    def test_weekly_range_from_monday_uses_previous_day_start(self):
        monday = date(2026, 8, 17)
        assert interval_range(StatisticIntervalChoices.WEEKLY, monday) == (
            date(2026, 8, 16),
            date(2026, 8, 22),
        )

    def test_weekly_range_from_saturday_start_of_week(self):
        saturday = date(2026, 8, 15)
        assert interval_range(StatisticIntervalChoices.WEEKLY, saturday) == (
            date(2026, 8, 9),
            date(2026, 8, 15),
        )

    def test_monthly_range_midmonth(self):
        assert interval_range(StatisticIntervalChoices.MONTHLY, date(2026, 1, 15)) == (
            date(2026, 1, 1),
            date(2026, 1, 31),
        )

    def test_monthly_range_february_non_leap(self):
        assert interval_range(StatisticIntervalChoices.MONTHLY, date(2026, 2, 28)) == (
            date(2026, 2, 1),
            date(2026, 2, 28),
        )

    def test_monthly_range_february_leap(self):
        assert interval_range(StatisticIntervalChoices.MONTHLY, date(2028, 2, 14)) == (
            date(2028, 2, 1),
            date(2028, 2, 29),
        )

    def test_monthly_range_last_day_of_year(self):
        assert interval_range(StatisticIntervalChoices.MONTHLY, date(2025, 12, 31)) == (
            date(2025, 12, 1),
            date(2025, 12, 31),
        )


class LocalDayStartTestCase(TestCase):
    def test_local_day_start_is_aware_local_midnight(self):
        value_date = date(2026, 8, 19)
        start = local_day_start(value_date)
        assert start.tzinfo is not None
        assert start.date() == value_date
        assert (start.hour, start.minute, start.second, start.microsecond) == (0, 0, 0, 0)

    def test_local_day_start_steps_one_day(self):
        value_date = date(2026, 8, 19)
        next_day = value_date + timedelta(days=1)
        assert local_day_start(next_day).date() == next_day

    def test_local_day_start_ordering(self):
        assert local_day_start(date(2026, 8, 20)) > local_day_start(date(2026, 8, 19))
