from __future__ import annotations

from django.test import TestCase

from django_spire.contrib.seeding.field.static import StaticFieldSeeder


class TestStaticFieldSeeder(TestCase):
    def test_seeds_static_fields(self) -> None:
        fields = {
            'category': ('static', 'books'),
            'in_stock': ('static', True)
        }
        seeder = StaticFieldSeeder(fields=fields)

        result = seeder.seed(count=3)

        assert len(result) == 3

        for row in result:
            assert row['category'] == 'books'
            assert row['in_stock'] is True
