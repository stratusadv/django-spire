from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.sms.exceptions import TwilioError
from django_spire.notification.sms.helper import TwilioSMSHelper
from django_spire.notification.sms.tests.factories import create_test_sms_notification


class TwilioSMSHelperTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = create_user(username='test_helper_user')
        self.sms_notification = create_test_sms_notification(user=self.user)
        self.mock_client = MagicMock()

    def test_format_phone_number_10_digits(self):
        result = TwilioSMSHelper._format_phone_number('5551234567')
        assert result == '+15551234567'

    def test_format_phone_number_11_digits_with_country_code(self):
        result = TwilioSMSHelper._format_phone_number('15551234567')
        assert result == '+15551234567'

    def test_format_phone_number_invalid_raises_error(self):
        with pytest.raises(TwilioError):
            TwilioSMSHelper._format_phone_number('123')

    def test_format_phone_number_too_long_raises_error(self):
        with pytest.raises(TwilioError):
            TwilioSMSHelper._format_phone_number('123456789012345')

    def test_message_format(self):
        helper = TwilioSMSHelper(
            self.sms_notification.notification,
            self.mock_client
        )
        expected = f'{self.sms_notification.notification.title}: {self.sms_notification.notification.body}'
        assert helper.message == expected

    def test_to_phone_number_formatted(self):
        helper = TwilioSMSHelper(
            self.sms_notification.notification,
            self.mock_client
        )
        assert helper.to_phone_number.startswith('+1')
