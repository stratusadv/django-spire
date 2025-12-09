from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.exceptions import (
    HelpDeskNotificationRecipientMissingEmailError,
    TicketEventNotificationTypeNotSupportedError,
)


class HelpDeskExceptionsTests(BaseTestCase):
    def test_ticket_event_notification_type_not_supported_error_is_type_error(self):
        assert issubclass(TicketEventNotificationTypeNotSupportedError, TypeError)

    def test_ticket_event_notification_type_not_supported_error_message(self):
        error = TicketEventNotificationTypeNotSupportedError('Test message')
        assert str(error) == 'Test message'

    def test_helpdesk_notification_recipient_missing_email_error_is_value_error(self):
        assert issubclass(HelpDeskNotificationRecipientMissingEmailError, ValueError)

    def test_helpdesk_notification_recipient_missing_email_error_message(self):
        error = HelpDeskNotificationRecipientMissingEmailError('Missing email')
        assert str(error) == 'Missing email'
