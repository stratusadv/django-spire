from __future__ import annotations

from django.test import TestCase

from django_spire.contrib.utils import truncate_string


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
