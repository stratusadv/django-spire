from __future__ import annotations

import pytest

from django.test import TestCase

from django_spire.core.utils import (
    get_callable_from_module_string_and_validate_arguments,
    get_object_from_module_string
)


class TestGetObjectFromModuleString(TestCase):
    def test_import_class(self) -> None:
        obj = get_object_from_module_string('django.test.TestCase')
        assert obj is TestCase

    def test_import_function(self) -> None:
        obj = get_object_from_module_string('os.path.join')
        assert callable(obj)

    def test_import_invalid_module(self) -> None:
        with pytest.raises(ImportError, match='Could not import module'):
            get_object_from_module_string('nonexistent.module.Object')

    def test_import_module_constant(self) -> None:
        obj = get_object_from_module_string('os.sep')
        assert isinstance(obj, str)


class TestGetCallableFromModuleStringAndValidateArguments(TestCase):
    def test_callable_with_missing_argument(self) -> None:
        with pytest.raises(TypeError, match='missing required argument'):
            get_callable_from_module_string_and_validate_arguments(
                'json.dumps',
                ['nonexistent_arg']
            )

    def test_callable_with_valid_arguments(self) -> None:
        callable_ = get_callable_from_module_string_and_validate_arguments(
            'json.dumps',
            ['obj']
        )
        assert callable(callable_)

    def test_invalid_module(self) -> None:
        with pytest.raises(ImportError, match='Could not import module'):
            get_callable_from_module_string_and_validate_arguments(
                'nonexistent.module.func',
                []
            )

    def test_non_callable_object(self) -> None:
        with pytest.raises(TypeError, match='is not callable'):
            get_callable_from_module_string_and_validate_arguments(
                'os.sep',
                []
            )
