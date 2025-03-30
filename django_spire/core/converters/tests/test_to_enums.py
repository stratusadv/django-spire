from enum import Enum
from unittest import TestCase

from django_spire.core.converters.to_enums import django_choices_to_enums


class TestDjangoChoicesToEnums(TestCase):

    def test_basic_conversion(self):
        """Test basic conversion with simple choices"""
        choices = [
            ('ACTIVE', 'Active'),
            ('INACTIVE', 'Inactive'),
            ('PENDING', 'Pending')
        ]

        ResultEnum = django_choices_to_enums('Status', choices)

        # Check if enum is created correctly
        self.assertTrue(issubclass(ResultEnum, Enum))
        self.assertEqual(ResultEnum.__name__, 'Status')

        # Check enum members
        self.assertEqual(ResultEnum.ACTIVE.value, 'ACTIVE')
        self.assertEqual(ResultEnum.INACTIVE.value, 'INACTIVE')
        self.assertEqual(ResultEnum.PENDING.value, 'PENDING')

        # Check number of members
        self.assertEqual(len(ResultEnum), 3)

    def test_empty_choices(self):
        """Test function with empty choices list"""
        choices = []
        ResultEnum = django_choices_to_enums('EmptyStatus', choices)

        self.assertTrue(issubclass(ResultEnum, Enum))
        self.assertEqual(ResultEnum.__name__, 'EmptyStatus')
        self.assertEqual(len(ResultEnum), 0)

    def test_single_choice(self):
        """Test with a single choice"""
        choices = [('OPEN', 'Open')]
        ResultEnum = django_choices_to_enums('SingleStatus', choices)

        self.assertTrue(issubclass(ResultEnum, Enum))
        self.assertEqual(ResultEnum.__name__, 'SingleStatus')
        self.assertEqual(ResultEnum.OPEN.value, 'OPEN')
        self.assertEqual(len(ResultEnum), 1)

    def test_duplicate_keys(self):
        """Test behavior with duplicate keys (should use last occurrence)"""
        choices = [
            ('STATUS', 'First'),
            ('STATUS', 'Second')
        ]
        ResultEnum = django_choices_to_enums('DuplicateStatus', choices)

        self.assertTrue(issubclass(ResultEnum, Enum))
        self.assertEqual(ResultEnum.STATUS.value, 'STATUS')
        self.assertEqual(len(ResultEnum), 1)

    def test_different_key_value(self):
        """Test when keys and values differ"""
        choices = [
            ('A', 'Alpha'),
            ('B', 'Beta'),
            ('G', 'Gamma')
        ]
        ResultEnum = django_choices_to_enums('Greek', choices)

        self.assertTrue(issubclass(ResultEnum, Enum))
        self.assertEqual(ResultEnum.A.value, 'A')
        self.assertEqual(ResultEnum.B.value, 'B')
        self.assertEqual(ResultEnum.G.value, 'G')
        self.assertEqual(len(ResultEnum), 3)
