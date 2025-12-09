from __future__ import annotations

import pytest

from django.test import TestCase

from django_spire.exceptions import DjangoSpireConfigurationError, DjangoSpireError


class TestDjangoSpireError(TestCase):
    def test_can_be_raised(self) -> None:
        with pytest.raises(DjangoSpireError):
            message = 'Test error'
            raise DjangoSpireError(message)

    def test_is_exception_subclass(self) -> None:
        assert issubclass(DjangoSpireError, Exception)

    def test_message(self) -> None:
        error = DjangoSpireError('Test error message')

        assert str(error) == 'Test error message'


class TestDjangoSpireConfigurationError(TestCase):
    def test_can_be_raised(self) -> None:
        with pytest.raises(DjangoSpireConfigurationError):
            message = 'Test error'
            raise DjangoSpireConfigurationError(message)

    def test_is_django_spire_error_subclass(self) -> None:
        assert issubclass(DjangoSpireConfigurationError, DjangoSpireError)

    def test_message(self) -> None:
        error = DjangoSpireConfigurationError('Configuration error message')

        assert str(error) == 'Configuration error message'
