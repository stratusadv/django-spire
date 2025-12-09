from __future__ import annotations

from django.test import TestCase

from django_spire.contrib.seeding.field.base import BaseFieldSeeder


class DummyFieldSeeder(BaseFieldSeeder):
    keyword = 'faker'

    def seed(self, model_seeder_cls=None, count: int = 1) -> list[dict]:
        return [{'fake': True} for _ in range(count)]


class TestBaseFieldSeeder(TestCase):
    def test_filter_fields(self) -> None:
        fields = {
            'name': ('faker', 'name'),
            'email': ('faker', 'email'),
            'description': ('llm', 'prompt')
        }
        seeder = DummyFieldSeeder(fields=fields)

        faker_fields = seeder.filter_fields('faker')

        assert 'name' in faker_fields
        assert 'email' in faker_fields
        assert 'description' not in faker_fields
