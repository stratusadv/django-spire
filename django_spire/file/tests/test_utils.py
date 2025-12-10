from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.utils import random_64_char_token


class Random64CharTokenTests(BaseTestCase):
    def test_returns_string(self):
        result = random_64_char_token()

        assert isinstance(result, str)

    def test_returns_64_characters(self):
        result = random_64_char_token()

        assert len(result) == 64

    def test_returns_hexadecimal(self):
        result = random_64_char_token()

        int(result, 16)

    def test_returns_unique_values(self):
        result1 = random_64_char_token()
        result2 = random_64_char_token()

        assert result1 != result2

    def test_returns_lowercase(self):
        result = random_64_char_token()

        assert result == result.lower()
