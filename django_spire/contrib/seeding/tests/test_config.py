from __future__ import annotations

import pytest

from unittest.mock import MagicMock

from django.test import TestCase

from django_spire.contrib.seeding.model.config import FieldsConfig


class TestFieldsConfig(TestCase):
    def setUp(self) -> None:
        self.model_class = MagicMock()

    def test_assign_defaults_adds_missing_fields(self) -> None:
        config = FieldsConfig(
            raw_fields={'name': ('static', 'test')},
            field_names=['name', 'email'],
            default_to='llm',
            model_class=self.model_class
        )

        assert 'email' in config.fields
        assert config.fields['email'] == ('llm',)

    def test_excluded_property(self) -> None:
        config = FieldsConfig(
            raw_fields={'name': 'exclude', 'email': ('exclude',)},
            field_names=['name', 'email', 'status'],
            default_to='llm',
            model_class=self.model_class
        )

        assert 'name' in config.excluded
        assert 'email' in config.excluded
        assert 'status' not in config.excluded

    def test_fields_are_ordered(self) -> None:
        config = FieldsConfig(
            raw_fields={'zebra': ('static', 'z'), 'apple': ('static', 'a')},
            field_names=['zebra', 'apple'],
            default_to='included',
            model_class=self.model_class
        )

        keys = list(config.fields.keys())

        assert keys == ['apple', 'zebra']

    def test_override_creates_new_config(self) -> None:
        config = FieldsConfig(
            raw_fields={'name': ('static', 'original')},
            field_names=['name', 'email'],
            default_to='llm',
            model_class=self.model_class
        )

        new_config = config.override({'name': ('static', 'overridden')})

        assert new_config is not config
        assert new_config.fields['name'] == ('static', 'overridden')

    def test_validate_raises_for_invalid_fields(self) -> None:
        with pytest.raises(ValueError, match='Invalid field name'):
            FieldsConfig(
                raw_fields={'invalid_field': ('static', 'test')},
                field_names=['name', 'email'],
                default_to='llm',
                model_class=self.model_class
            )
