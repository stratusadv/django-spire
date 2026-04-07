from __future__ import annotations

import unittest

from django.test import TestCase

from django_spire.contrib.utils import truncate_string, format_duration


class TestTruncateString(TestCase):
    def test_returns_original_when_equal_to_length(self) -> None:
        result = truncate_string('hello', 5)

        assert result == 'hello'

    def test_returns_original_when_shorter_than_length(self) -> None:
        result = truncate_string('hi', 10)

        assert result == 'hi'

    def test_truncates_when_longer_than_length(self) -> None:
        result = truncate_string('hello world', 8)

        assert result == 'hello...'

    def test_truncates_with_ellipsis(self) -> None:
        result = truncate_string('this is a long string', 10)

        assert result.endswith('...')

    def test_truncated_length_equals_specified_length(self) -> None:
        result = truncate_string('this is a long string', 10)

        assert len(result) == 10

    def test_empty_string(self) -> None:
        result = truncate_string('', 5)

        assert result == ''


class HumanizeSecondsDurationTestCase(unittest.TestCase):

    def test_format_duration(self):
        test_value = 65250367
        expected_result = '2 years, 3 weeks, 4 days, 5 hours, 6 minutes, 7 seconds'
        result = format_duration(
            amount=test_value,
        )
        assert result == expected_result

    def test_format_duration_short(self):
        test_value = 65250367
        expected_result = '2y 3w 4d 5h 6m 7s'
        result = format_duration(
            amount=test_value,
            is_short_form=True,
        )
        assert result == expected_result

    def test_format_duration_min_unit(self):
        test_value = 5430  # This is 1h 30m 30s
        expected_result = '1 hour, 30 minutes'
        result = format_duration(
            amount=test_value,
            min_unit='minute',
        )
        assert result == expected_result

    def test_format_duration_min_unit_short(self):
        test_value = 5430  # This is 1h 30m 30s
        expected_result = '1h 30m'
        result = format_duration(
            amount=test_value,
            min_unit='minute',
            is_short_form=True,
        )
        assert result == expected_result

    def test_format_duration_included_units(self):
        test_value = 619200
        expected_result = '7 days, 4 hours'
        result = format_duration(
            amount=test_value,
            included_units=['day', 'hour'],
        )
        assert result == expected_result

    def test_format_duration_included_units_short(self):
        test_value = 619200
        expected_result = '7d 4h'
        result = format_duration(
            amount=test_value,
            included_units=['day', 'hour'],
            is_short_form=True,
        )
        assert result == expected_result

    def test_format_duration_with_min_unit_included_units_short(self):
        test_value = 619200
        expected_result = '7d'
        result = format_duration(
            amount=test_value,
            included_units=['day', 'hour'],
            min_unit='day',
            is_short_form=True,
        )
        assert result == expected_result

    def test_format_duration_days_to_hours(self):
        test_value = 1.5
        expected_result = '36 hours'
        result = format_duration(
            amount=test_value,
            start_unit='day',
            included_units=['hour'],
        )
        assert result == expected_result

    def test_format_duration_days_to_hours_short(self):
        test_value = 1.5
        expected_result = '36h'
        result = format_duration(
            amount=test_value,
            start_unit='day',
            included_units=['hour'],
            is_short_form=True,
        )
        assert result == expected_result