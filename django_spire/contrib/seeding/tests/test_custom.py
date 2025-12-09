from __future__ import annotations

import pytest

from django.test import TestCase
from django.utils import timezone

from django_spire.contrib.seeding.field.custom import CustomFieldSeeder


class TestCustomFieldSeeder(TestCase):
    def test_date_time_between_returns_aware_datetime(self) -> None:
        seeder = CustomFieldSeeder(fields={})

        result = seeder.date_time_between(start_date='-30d', end_date='now')

        assert timezone.is_aware(result)

    def test_in_order_cycles_through_values(self) -> None:
        seeder = CustomFieldSeeder(fields={})
        values = ['a', 'b', 'c']

        assert seeder.in_order(values, index=0) == 'a'
        assert seeder.in_order(values, index=1) == 'b'
        assert seeder.in_order(values, index=2) == 'c'
        assert seeder.in_order(values, index=3) == 'a'

    def test_in_order_raises_for_empty_list(self) -> None:
        seeder = CustomFieldSeeder(fields={})

        with pytest.raises(ValueError, match='Cannot select from empty values list'):
            seeder.in_order(values=[], index=0)

    def test_keyword_is_custom(self) -> None:
        assert CustomFieldSeeder.keyword == 'custom'
