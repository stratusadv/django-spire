from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.sms.exceptions import (
    SmsNotificationError,
    SmsTemporaryMediaError,
    TwilioAPIConcurrentError,
    TwilioError,
)


class SmsExceptionsTests(BaseTestCase):
    def test_sms_notification_error_message(self):
        error = SmsNotificationError('SMS error')
        assert str(error) == 'SMS error'

    def test_sms_temporary_media_error_message(self):
        error = SmsTemporaryMediaError('Media error')
        assert str(error) == 'Media error'

    def test_twilio_error_message(self):
        error = TwilioError('Twilio error')
        assert str(error) == 'Twilio error'

    def test_twilio_api_concurrent_error_message(self):
        error = TwilioAPIConcurrentError('Concurrent error')
        assert str(error) == 'Concurrent error'
