from __future__ import annotations

from unittest.mock import MagicMock

from django.test import TestCase

from django_spire.contrib.seeding.field.override import FieldOverride


class TestFieldOverride(TestCase):
    def setUp(self) -> None:
        self.seeder_class = MagicMock()
        self.seeder_class.seed.return_value = [{'name': 'test'}]

    def test_filter_returns_self(self) -> None:
        override = FieldOverride(self.seeder_class)

        result = override.filter(name='test')

        assert result is override

    def test_filter_updates_overrides(self) -> None:
        override = FieldOverride(self.seeder_class)

        override.filter(name='test', status='active')

        assert override.overrides == {'name': 'test', 'status': 'active'}

    def test_getattr_delegates_to_seeder_class(self) -> None:
        self.seeder_class.some_attribute = 'value'
        override = FieldOverride(self.seeder_class)

        result = override.some_attribute

        assert result == 'value'

    def test_init_sets_seeder_class(self) -> None:
        override = FieldOverride(self.seeder_class)

        assert override.seeder_class is self.seeder_class

    def test_init_sets_empty_overrides(self) -> None:
        override = FieldOverride(self.seeder_class)

        assert override.overrides == {}

    def test_seed_calls_seeder_class_seed(self) -> None:
        override = FieldOverride(self.seeder_class)
        override.filter(name='override_value')

        override.seed(count=2)

        self.seeder_class.seed.assert_called_once_with(
            count=2,
            fields={'name': 'override_value'}
        )

    def test_seed_returns_seeder_class_result(self) -> None:
        override = FieldOverride(self.seeder_class)

        result = override.seed(count=1)

        assert result == [{'name': 'test'}]
