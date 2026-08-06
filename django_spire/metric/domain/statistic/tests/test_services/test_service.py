from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.utils import timezone

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.models import StatisticValue
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
)


class StatisticProcessorServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def test_add_value_default_date(self):
        statistic_value = self.statistic.services.processor.add_value(reference='/home/')
        assert statistic_value.reference == '/home/'
        assert statistic_value.date == timezone.localdate()
        assert statistic_value.value == Decimal(1)

    def test_add_value_accumulates_on_same_reference_and_date(self):
        self.statistic.services.processor.add_value(reference='/home/')
        self.statistic.services.processor.add_value(reference='/home/')
        self.statistic.services.processor.add_value(reference='/home/')

        statistic_value = StatisticValue.objects.get(
            statistic=self.statistic, reference='/home/', date=timezone.localdate()
        )
        assert statistic_value.value == Decimal(3)

    def test_add_value_creates_new_entry_for_new_reference(self):
        self.statistic.services.processor.add_value(reference='/home/')
        self.statistic.services.processor.add_value(reference='/dashboard/')

        assert StatisticValue.objects.count() == 2

    def test_add_value_custom_value(self):
        statistic_value = self.statistic.services.processor.add_value(
            reference='/home/', value=Decimal(5)
        )
        assert statistic_value.value == Decimal(5)

    def test_add_value_custom_date(self):
        arbitrary_date = date(2024, 1, 1)
        self.statistic.services.processor.add_value(reference='/home/', value_date=arbitrary_date)
        self.statistic.services.processor.add_value(reference='/home/', value_date=arbitrary_date)

        statistic_value = StatisticValue.objects.get(
            statistic=self.statistic, reference='/home/', date=arbitrary_date
        )
        assert statistic_value.value == Decimal(2)

    def test_same_reference_different_dates_are_separate(self):
        self.statistic.services.processor.add_value(reference='/home/')
        self.statistic.services.processor.add_value(reference='/home/', value_date=date(2024, 1, 1))

        assert StatisticValue.objects.filter(reference='/home/').count() == 2

    def test_increment(self):
        self.statistic.services.processor.increment(reference='/home/')
        statistic_value = StatisticValue.objects.get(reference='/home/')
        assert statistic_value.value == Decimal(1)

    def test_decrement(self):
        self.statistic.services.processor.add_value(reference='/home/', value=Decimal(5))
        self.statistic.services.processor.decrement(reference='/home/')
        statistic_value = StatisticValue.objects.get(reference='/home/')
        assert statistic_value.value == Decimal(4)

    def test_subtract_value(self):
        self.statistic.services.processor.add_value(reference='/home/', value=Decimal(5))
        self.statistic.services.processor.subtract_value(reference='/home/', value=Decimal(2))
        statistic_value = StatisticValue.objects.get(reference='/home/')
        assert statistic_value.value == Decimal(3)


class StatisticTransformationServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)
        self.today = timezone.localdate()

    def seed_values(self) -> None:
        self.statistic.services.processor.add_value(reference='/home/', value=Decimal(2))
        self.statistic.services.processor.add_value(reference='/dashboard/', value=Decimal(3))
        self.statistic.services.processor.add_value(
            reference='/pricing/', value=Decimal(5), value_date=date(2024, 1, 1)
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

    def test_total_for_date_sums_all_references(self):
        self.seed_values()
        total = self.statistic.services.transformation.total_for_date(self.today)
        assert total == Decimal(5)

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
