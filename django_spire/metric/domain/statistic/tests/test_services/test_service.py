from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

import pytest

from django_spire.contrib.constructor.service.exceptions import ServiceError
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.constants import (
    StatisticIntervalChoices,
    StatisticValueTypeChoices,
)
from django_spire.metric.domain.statistic.models import Statistic, StatisticValue
from django_spire.metric.domain.statistic.services.service import StatisticService
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
)

_NAIVE_STUB = datetime(2024, 1, 1, 12, 0)  # noqa: DTZ001


def aware(value_date: date, hour: int = 12) -> datetime:
    return timezone.make_aware(
        datetime(value_date.year, value_date.month, value_date.day, hour)  # noqa: DTZ001
    )


class StatisticProcessorServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def test_add_value_rejects_sub_domain_outside_domain(self):
        foreign_domain = create_test_domain(name='foreign_domain')
        foreign_sub_domain = create_test_subdomain(domain=foreign_domain, name='foreign')

        with pytest.raises(ServiceError):
            self.statistic.services.processor.add_value(
                reference='/home/', sub_domain=foreign_sub_domain
            )

        assert self.statistic.values.count() == 0

    def test_add_value_records_arrival_time(self):
        statistic_value = self.statistic.services.processor.add_value(
            reference='/home/', sub_domain=self.sub_domain
        )
        assert statistic_value.reference == '/home/'
        assert statistic_value.sub_domain == self.sub_domain
        assert statistic_value.timestamp.tzinfo is not None
        assert timezone.localtime(statistic_value.timestamp).date() == timezone.localdate()
        assert statistic_value.value == Decimal(1)

    def test_add_value_returns_field_precision(self):
        statistic_value = self.statistic.services.processor.add_value(
            reference='/home/', sub_domain=self.sub_domain
        )
        assert str(statistic_value.value) == '1.0000'

    def test_add_value_appends_one_row_per_call(self):
        for _ in range(3):
            self.statistic.services.processor.add_value(
                reference='/home/', sub_domain=self.sub_domain
            )

        assert StatisticValue.objects.filter(reference='/home/').count() == 3
        assert self.statistic.values.total() == Decimal(3)

    def test_add_value_different_sub_domain_separate_rows(self):
        other_sub_domain = create_test_subdomain(domain=self.domain, name='other_subdomain')
        self.statistic.services.processor.add_value(reference='/home/', sub_domain=self.sub_domain)
        self.statistic.services.processor.add_value(reference='/home/', sub_domain=other_sub_domain)

        assert StatisticValue.objects.count() == 2
        assert self.statistic.values.for_sub_domain(self.sub_domain).count() == 1
        assert self.statistic.values.for_sub_domain(other_sub_domain).count() == 1

    def test_add_value_custom_value(self):
        statistic_value = self.statistic.services.processor.add_value(
            reference='/home/', sub_domain=self.sub_domain, value=Decimal(5)
        )
        assert statistic_value.value == Decimal(5)

    def test_add_value_naive_timestamp_becomes_local_aware(self):
        statistic_value = self.statistic.services.processor.add_value(
            reference='/home/', sub_domain=self.sub_domain, value_timestamp=_NAIVE_STUB
        )
        assert statistic_value.timestamp == timezone.make_aware(_NAIVE_STUB)
        assert self.statistic.values.for_date(date(2024, 1, 1)).count() == 1

    def test_add_value_aware_timestamp_stored_as_given(self):
        stamp = timezone.make_aware(_NAIVE_STUB)
        statistic_value = self.statistic.services.processor.add_value(
            reference='/home/', sub_domain=self.sub_domain, value_timestamp=stamp
        )
        assert statistic_value.timestamp == stamp

    def test_same_reference_different_times_are_separate(self):
        self.statistic.services.processor.add_value(reference='/home/', sub_domain=self.sub_domain)
        self.statistic.services.processor.add_value(
            reference='/home/', sub_domain=self.sub_domain, value_timestamp=_NAIVE_STUB
        )

        assert StatisticValue.objects.filter(reference='/home/').count() == 2

    def test_increment(self):
        statistic_value = self.statistic.services.processor.increment(
            reference='/home/', sub_domain=self.sub_domain
        )
        assert statistic_value.value == Decimal(1)
        assert StatisticValue.objects.count() == 1

    def test_decrement(self):
        self.statistic.services.processor.add_value(
            reference='/home/', sub_domain=self.sub_domain, value=Decimal(5)
        )
        self.statistic.services.processor.decrement(reference='/home/', sub_domain=self.sub_domain)
        assert StatisticValue.objects.count() == 2
        assert self.statistic.values.total() == Decimal(4)

    def test_subtract_value(self):
        self.statistic.services.processor.add_value(
            reference='/home/', sub_domain=self.sub_domain, value=Decimal(5)
        )
        self.statistic.services.processor.subtract_value(
            reference='/home/', sub_domain=self.sub_domain, value=Decimal(2)
        )
        assert StatisticValue.objects.count() == 2
        assert self.statistic.values.total() == Decimal(3)
        assert StatisticValue.objects.filter(reference='/home/', value=Decimal(-2)).count() == 1


class StatisticTransformationServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.other_sub_domain = create_test_subdomain(domain=self.domain, name='other_subdomain')
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)
        self.today = timezone.localdate()

    def seed_values(self) -> None:
        self.statistic.services.processor.add_value(
            reference='/home/', value=Decimal(2), sub_domain=self.sub_domain
        )
        self.statistic.services.processor.add_value(
            reference='/dashboard/', value=Decimal(3), sub_domain=self.other_sub_domain
        )
        self.statistic.services.processor.add_value(
            reference='/pricing/',
            value=Decimal(5),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2024, 1, 1)),
        )

    def test_values_for_date_returns_all_references(self):
        self.seed_values()
        values = self.statistic.services.transformation.values_for_date(self.today)
        assert values.count() == 2
        assert {value.reference for value in values} == {'/home/', '/dashboard/'}

    def test_values_for_date_defaults_to_today(self):
        self.seed_values()
        values = self.statistic.services.transformation.values_for_date()
        assert values.count() == 2

    def test_deleted_statistic_value_queryset_is_empty(self):
        self.seed_values()
        self.statistic.set_deleted()

        assert self.statistic.services.transformation.value_queryset().count() == 0
        assert self.statistic.services.transformation.values_for_date(self.today).count() == 0
        assert self.statistic.services.transformation.daily_summary(self.today, self.today) == {}
        assert self.statistic.services.transformation.interval_summary(self.today, self.today) == {}

    def test_deleted_statistic_total_for_date_is_zero(self):
        self.seed_values()
        self.statistic.set_deleted()

        assert self.statistic.services.transformation.total_for_date(self.today) == Decimal(0)
        assert self.statistic.services.transformation.total_between(
            self.today, self.today
        ) == Decimal(0)

    def test_total_for_date_sums_all_references(self):
        self.seed_values()
        total = self.statistic.services.transformation.total_for_date(self.today)
        assert total == Decimal(5)

    def test_total_for_date_filters_sub_domain(self):
        self.seed_values()
        total = self.statistic.services.transformation.total_for_date(
            self.today, sub_domain=self.sub_domain
        )
        assert total == Decimal(2)
        total = self.statistic.services.transformation.total_for_date(
            self.today, sub_domain=self.other_sub_domain
        )
        assert total == Decimal(3)

    def test_total_between(self):
        self.seed_values()
        total = self.statistic.services.transformation.total_between(
            date(2024, 1, 1), date(2024, 1, 31)
        )
        assert total == Decimal(5)

    def test_daily_summary(self):
        self.seed_values()
        summary = self.statistic.services.transformation.daily_summary(
            date(2024, 1, 1), date(2024, 1, 31)
        )
        assert summary == {date(2024, 1, 1): Decimal(5)}

    def test_daily_summary_filters_sub_domain(self):
        self.seed_values()
        summary = self.statistic.services.transformation.daily_summary(
            date(2024, 1, 1), date(2024, 1, 31), sub_domain=self.other_sub_domain
        )
        assert summary == {}


class StatisticIntervalTransformationServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)

    def test_weekly_interval_bounds(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        assert statistic.services.transformation.interval_bounds(date(2026, 8, 19)) == (
            date(2026, 8, 16),
            date(2026, 8, 22),
        )

    def test_monthly_interval_bounds(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.MONTHLY
        )
        assert statistic.services.transformation.interval_bounds(date(2026, 1, 15)) == (
            date(2026, 1, 1),
            date(2026, 1, 31),
        )

    def test_values_for_interval_returns_all_references_in_bucket(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(2),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 16)),
        )
        statistic.services.processor.add_value(
            reference='/dashboard/',
            value=Decimal(3),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 19)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(5),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 23)),
        )

        values = statistic.services.transformation.values_for_interval(date(2026, 8, 19))
        assert values.count() == 2
        assert {value.reference for value in values} == {'/home/', '/dashboard/'}

    def test_values_for_interval_filters_sub_domain(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        other_sub_domain = create_test_subdomain(domain=self.domain, name='other_subdomain')
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(2),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 16)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(3),
            sub_domain=other_sub_domain,
            value_timestamp=aware(date(2026, 8, 16)),
        )

        values = statistic.services.transformation.values_for_interval(
            date(2026, 8, 19), sub_domain=other_sub_domain
        )
        assert values.count() == 1
        assert values.first().sub_domain == other_sub_domain

    def test_total_for_interval_sums_bucket_across_references(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(2),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 16)),
        )
        statistic.services.processor.add_value(
            reference='/dashboard/',
            value=Decimal(3),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 19)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(5),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 23)),
        )

        assert statistic.services.transformation.total_for_interval(date(2026, 8, 19)) == Decimal(5)

    def test_total_for_interval_monthly(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.MONTHLY
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(2),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 1, 1)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(3),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 1, 31)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(5),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 2, 1)),
        )

        assert statistic.services.transformation.total_for_interval(date(2026, 1, 15)) == Decimal(5)
        assert statistic.services.transformation.total_for_interval(date(2026, 2, 15)) == Decimal(5)

    def test_total_for_interval_percentage_is_moving_average(self):
        statistic = create_test_statistic(
            group=self.group, value_type=StatisticValueTypeChoices.PERCENTAGE
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(4),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 23)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(6),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 24)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(100),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 1)),
        )

        assert statistic.services.transformation.total_for_interval(date(2026, 8, 24)) == Decimal(5)

    def test_total_for_interval_percentage_averages_daily_before_window(self):
        statistic = create_test_statistic(
            group=self.group, value_type=StatisticValueTypeChoices.PERCENTAGE
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(6),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 23)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(2),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 24), 10),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(10),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 24), 14),
        )

        assert statistic.services.transformation.total_for_interval(date(2026, 8, 24)) == Decimal(6)

    def test_total_for_interval_percentage_without_data_is_zero(self):
        statistic = create_test_statistic(
            group=self.group, value_type=StatisticValueTypeChoices.PERCENTAGE
        )
        assert statistic.services.transformation.total_for_interval(date(2026, 8, 24)) == Decimal(0)

    def test_interval_summary_weekly_groups_by_bucket_start(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(1),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 16)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(2),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 19)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(3),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 23)),
        )

        summary = statistic.services.transformation.interval_summary(
            date(2026, 8, 9), date(2026, 8, 29)
        )
        assert summary == {date(2026, 8, 16): Decimal(3), date(2026, 8, 23): Decimal(3)}

    def test_interval_summary_monthly_groups_by_month_start(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.MONTHLY
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(1),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 1, 15)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(2),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 2, 2)),
        )

        summary = statistic.services.transformation.interval_summary(
            date(2026, 1, 1), date(2026, 2, 28)
        )
        assert summary == {date(2026, 1, 1): Decimal(1), date(2026, 2, 1): Decimal(2)}

    def test_interval_summary_daily_matches_daily_summary(self):
        statistic = create_test_statistic(group=self.group, interval=StatisticIntervalChoices.DAILY)
        value_dates = [date(2026, 8, 16), date(2026, 8, 16), date(2026, 8, 19), date(2026, 8, 23)]
        for idx, value_date in enumerate(value_dates, start=1):
            statistic.services.processor.add_value(
                reference='/home/',
                value=Decimal(idx),
                sub_domain=self.sub_domain,
                value_timestamp=aware(value_date),
            )

        start_date, end_date = date(2026, 8, 10), date(2026, 8, 31)
        summary = statistic.services.transformation.interval_summary(start_date, end_date)
        assert summary == statistic.services.transformation.daily_summary(start_date, end_date)

    def test_interval_summary_daily_groups_by_day(self):
        statistic = create_test_statistic(group=self.group, interval=StatisticIntervalChoices.DAILY)
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(1),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 16)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(2),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 16)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(4),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 19)),
        )

        summary = statistic.services.transformation.interval_summary(
            date(2026, 8, 10), date(2026, 8, 31)
        )
        assert summary == {date(2026, 8, 16): Decimal(3), date(2026, 8, 19): Decimal(4)}

    def test_interval_summary_percentage_averages_raw_rows_not_daily_means(self):
        statistic = create_test_statistic(
            group=self.group,
            interval=StatisticIntervalChoices.WEEKLY,
            value_type=StatisticValueTypeChoices.PERCENTAGE,
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(3),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 19)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(1),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 20)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(1),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 20), 14),
        )

        summary = statistic.services.transformation.interval_summary(
            date(2026, 8, 10), date(2026, 8, 31)
        )
        assert summary == {date(2026, 8, 16): Decimal(5) / Decimal(3)}

    def test_interval_summary_is_empty_without_values(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        assert (
            statistic.services.transformation.interval_summary(date(2026, 8, 10), date(2026, 8, 31))
            == {}
        )

    def test_interval_summary_is_empty_outside_range(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(1),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 8, 16)),
        )
        assert (
            statistic.services.transformation.interval_summary(date(2026, 9, 1), date(2026, 9, 30))
            == {}
        )


class StatisticRecordServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def test_record_creates_value(self):
        statistic_value = StatisticService.record(
            self.statistic.key, self.sub_domain.key, '/home/', value=Decimal(5)
        )

        assert statistic_value.statistic == self.statistic
        assert statistic_value.sub_domain == self.sub_domain
        assert statistic_value.reference == '/home/'
        assert statistic_value.value == Decimal(5)
        assert StatisticValue.objects.count() == 1

    def test_record_default_value_is_one(self):
        statistic_value = StatisticService.record(self.statistic.key, self.sub_domain.key, '/home/')

        assert statistic_value.value == Decimal(1)

    def test_record_unknown_statistic_raises(self):
        with pytest.raises(ServiceError):
            StatisticService.record('missing-statistic', self.sub_domain.key, '/home/')

    def test_record_unknown_sub_domain_raises(self):
        with pytest.raises(ServiceError):
            StatisticService.record(self.statistic.key, 'missing-sub-domain', '/home/')

    def test_record_sub_domain_foreign_domain_raises(self):
        foreign_domain = create_test_domain(name='foreign_domain')
        foreign_sub_domain = create_test_subdomain(domain=foreign_domain, name='foreign')

        with pytest.raises(ServiceError):
            StatisticService.record(self.statistic.key, foreign_sub_domain.key, '/home/')

    def test_record_model_classmethod_delegates(self):
        statistic_value = Statistic.record(self.statistic.key, self.sub_domain.key, '/home/')

        assert statistic_value.value == Decimal(1)
        assert StatisticValue.objects.count() == 1

    def test_record_inserts_blind_in_single_statement(self):
        with CaptureQueriesContext(connection) as context:
            StatisticService.record(self.statistic.key, self.sub_domain.key, '/home/')

        insert = context.captured_queries[0]
        assert insert['sql'].startswith('INSERT')
        assert 'SELECT' in insert['sql']
        assert len(context) == 2
