from __future__ import annotations

from enum import Enum
from unittest import TestCase

from django_spire.core.converters.to_enums import django_choices_to_enums


class TestDjangoChoicesToEnums(TestCase):
    def test_basic_conversion(self) -> None:
        """Test basic conversion with simple choices"""

        choices = [
            ('ACTIVE', 'Active'),
            ('INACTIVE', 'Inactive'),
            ('PENDING', 'Pending')
        ]

        ResultEnum = django_choices_to_enums('Status', choices)

        assert issubclass(ResultEnum, Enum)
        assert ResultEnum.__name__ == 'Status'

        assert ResultEnum.ACTIVE.value == 'ACTIVE'
        assert ResultEnum.INACTIVE.value == 'INACTIVE'
        assert ResultEnum.PENDING.value == 'PENDING'

        assert len(ResultEnum) == 3

    def test_different_key_value(self) -> None:
        """Test when keys and values differ"""

        choices = [
            ('A', 'Alpha'),
            ('B', 'Beta'),
            ('G', 'Gamma')
        ]

        ResultEnum = django_choices_to_enums('Greek', choices)

        assert issubclass(ResultEnum, Enum)
        assert ResultEnum.A.value == 'A'
        assert ResultEnum.B.value == 'B'
        assert ResultEnum.G.value == 'G'
        assert len(ResultEnum) == 3

    def test_duplicate_keys(self) -> None:
        """Test behavior with duplicate keys (should use last occurrence)"""

        choices = [
            ('STATUS', 'First'),
            ('STATUS', 'Second')
        ]

        ResultEnum = django_choices_to_enums('DuplicateStatus', choices)

        assert issubclass(ResultEnum, Enum)
        assert ResultEnum.STATUS.value == 'STATUS'
        assert len(ResultEnum) == 1

    def test_empty_choices(self) -> None:
        """Test function with empty choices list"""

        choices = []
        ResultEnum = django_choices_to_enums('EmptyStatus', choices)

        assert issubclass(ResultEnum, Enum)
        assert ResultEnum.__name__ == 'EmptyStatus'
        assert len(ResultEnum) == 0

    def test_lowercase_keys_converted_to_uppercase(self) -> None:
        """Test that lowercase keys are converted to uppercase"""

        choices = [
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ]

        ResultEnum = django_choices_to_enums('Status', choices)

        assert hasattr(ResultEnum, 'ACTIVE')
        assert hasattr(ResultEnum, 'INACTIVE')
        assert ResultEnum.ACTIVE.value == 'active'
        assert ResultEnum.INACTIVE.value == 'inactive'

    def test_single_choice(self) -> None:
        """Test with a single choice"""

        choices = [('OPEN', 'Open')]
        ResultEnum = django_choices_to_enums('SingleStatus', choices)

        assert issubclass(ResultEnum, Enum)
        assert ResultEnum.__name__ == 'SingleStatus'
        assert ResultEnum.OPEN.value == 'OPEN'
        assert len(ResultEnum) == 1
