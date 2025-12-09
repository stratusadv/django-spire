from __future__ import annotations

from django.test import TestCase

from django_spire.contrib.seeding.field.callable import CallableFieldSeeder


class TestCallableFieldSeeder(TestCase):
    def test_seeds_callable_fields(self) -> None:
        fields = {
            'timestamp': lambda: '2024-01-01 12:00:00',
            'status': lambda: 'active'
        }
        seeder = CallableFieldSeeder(fields=fields)

        result = seeder.seed(None, count=3)

        assert len(result) == 3

        for row in result:
            assert row['timestamp'] == '2024-01-01 12:00:00'
            assert row['status'] == 'active'
