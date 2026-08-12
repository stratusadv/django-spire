from __future__ import annotations

from django_spire.auth.sms.utils import phone_number_format_display, phone_number_normalize
from django_spire.core.tests.test_cases import BaseTestCase


class SMSUtilsTests(BaseTestCase):
    @staticmethod
    def test_phone_number_normalize_local_10_digits() -> None:
        assert phone_number_normalize('5878004122') == '+15878004122'

    @staticmethod
    def test_phone_number_normalize_international_11_digits() -> None:
        assert phone_number_normalize('15878004122') == '+15878004122'

    @staticmethod
    def test_phone_number_normalize_with_country_code() -> None:
        assert phone_number_normalize('+1 (587) 800-4122') == '+15878004122'

    @staticmethod
    def test_phone_number_normalize_invalid_returns_none() -> None:
        assert phone_number_normalize('58780041') is None
        assert phone_number_normalize('') is None
        assert phone_number_normalize(None) is None

    @staticmethod
    def test_phone_number_format_display() -> None:
        assert phone_number_format_display('+15878004122') == '(587) 800-4122'
        assert phone_number_format_display('+1 (587) 800-4122') == '(587) 800-4122'

    @staticmethod
    def test_phone_number_format_display_invalid_returns_original() -> None:
        assert phone_number_format_display('58780041') == '58780041'
        assert phone_number_format_display('') == ''
        assert phone_number_format_display(None) == ''
