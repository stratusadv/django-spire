from __future__ import annotations

import pytest

from django.test import TestCase

from django_spire.utils import (
    app_is_installed,
    get_class_from_string,
    get_class_name_from_class,
)


class TestAppIsInstalled(TestCase):
    def test_installed_app_returns_true(self) -> None:
        result = app_is_installed('auth')

        assert result is True

    def test_not_installed_app_returns_false(self) -> None:
        result = app_is_installed('nonexistent_app')

        assert result is False


class TestGetClassFromString(TestCase):
    def test_imports_class(self) -> None:
        result = get_class_from_string('django.test.TestCase')

        assert result is TestCase

    def test_invalid_class_string_raises_exception(self) -> None:
        with pytest.raises(Exception, match='not a valid class string'):
            get_class_from_string('InvalidString')

    def test_nonexistent_module_raises_exception(self) -> None:
        with pytest.raises(ModuleNotFoundError):
            get_class_from_string('nonexistent.module.ClassName')


class TestGetClassNameFromClass(TestCase):
    def test_returns_full_class_path(self) -> None:
        result = get_class_name_from_class(TestCase)

        assert result == 'django.test.testcases.TestCase'

    def test_returns_string(self) -> None:
        result = get_class_name_from_class(TestCase)

        assert isinstance(result, str)

    def test_contains_module_and_class_name(self) -> None:
        result = get_class_name_from_class(TestCase)

        assert 'TestCase' in result
        assert 'django' in result
