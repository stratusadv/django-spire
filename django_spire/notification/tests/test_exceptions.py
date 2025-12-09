from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.exceptions import DjangoSpireError
from django_spire.notification.app.exceptions import AppNotificationError
from django_spire.notification.email.exceptions import EmailNotificationError
from django_spire.notification.exceptions import NotificationError
from django_spire.notification.sms.exceptions import (
    SmsNotificationError,
    SmsTemporaryMediaError,
    TwilioAPIConcurrentError,
    TwilioError,
)


class NotificationExceptionsTests(BaseTestCase):
    def test_notification_error_is_django_spire_error(self):
        assert issubclass(NotificationError, DjangoSpireError)

    def test_notification_error_message(self):
        error = NotificationError('Test error')
        assert str(error) == 'Test error'


class AppNotificationExceptionsTests(BaseTestCase):
    def test_app_notification_error_is_django_spire_error(self):
        assert issubclass(AppNotificationError, DjangoSpireError)

    def test_app_notification_error_message(self):
        error = AppNotificationError('Test error')
        assert str(error) == 'Test error'


class EmailNotificationExceptionsTests(BaseTestCase):
    def test_email_notification_error_is_django_spire_error(self):
        assert issubclass(EmailNotificationError, DjangoSpireError)

    def test_email_notification_error_message(self):
        error = EmailNotificationError('Test error')
        assert str(error) == 'Test error'


class SmsNotificationExceptionsTests(BaseTestCase):
    def test_sms_notification_error_is_django_spire_error(self):
        assert issubclass(SmsNotificationError, DjangoSpireError)

    def test_sms_notification_error_message(self):
        error = SmsNotificationError('Test error')
        assert str(error) == 'Test error'

    def test_sms_temporary_media_error_is_sms_notification_error(self):
        assert issubclass(SmsTemporaryMediaError, SmsNotificationError)

    def test_twilio_error_is_exception(self):
        assert issubclass(TwilioError, Exception)

    def test_twilio_api_concurrent_error_is_twilio_error(self):
        assert issubclass(TwilioAPIConcurrentError, TwilioError)
