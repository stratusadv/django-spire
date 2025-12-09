from __future__ import annotations

from django.test import TestCase

from django_spire.contrib.seeding.field.enums import FieldSeederTypesEnum
from django_spire.contrib.seeding.model.enums import ModelSeederDefaultsEnum


class TestFieldSeederTypesEnum(TestCase):
    def test_callable_value(self) -> None:
        assert FieldSeederTypesEnum.CALLABLE == 'callable'

    def test_custom_value(self) -> None:
        assert FieldSeederTypesEnum.CUSTOM == 'custom'

    def test_faker_value(self) -> None:
        assert FieldSeederTypesEnum.FAKER == 'faker'

    def test_is_str_enum(self) -> None:
        assert isinstance(FieldSeederTypesEnum.LLM, str)

    def test_llm_value(self) -> None:
        assert FieldSeederTypesEnum.LLM == 'llm'

    def test_static_value(self) -> None:
        assert FieldSeederTypesEnum.STATIC == 'static'


class TestModelSeederDefaultsEnum(TestCase):
    def test_faker_value(self) -> None:
        assert ModelSeederDefaultsEnum.FAKER == 'faker'

    def test_included_value(self) -> None:
        assert ModelSeederDefaultsEnum.INCLUDED == 'included'

    def test_is_str_enum(self) -> None:
        assert isinstance(ModelSeederDefaultsEnum.LLM, str)

    def test_llm_value(self) -> None:
        assert ModelSeederDefaultsEnum.LLM == 'llm'
