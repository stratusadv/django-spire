from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.enums import TicketEventType
from django_spire.help_desk.exceptions import (
    HelpDeskNotificationRecipientMissingEmailError,
    TicketEventNotificationTypeNotSupportedError,
)
from django_spire.notification.choices import NotificationTypeChoices


class HelpDeskExceptionsTests(BaseTestCase):
    def test_ticket_event_notification_type_not_supported_error_is_type_error(self):
        assert issubclass(TicketEventNotificationTypeNotSupportedError, TypeError)

    def test_ticket_event_notification_type_not_supported_error_message(self):
        error = TicketEventNotificationTypeNotSupportedError(
            TicketEventType.NEW,
            NotificationTypeChoices.SMS
        )
        assert 'Event type' in str(error)
        assert 'Notification type' in str(error)

    def test_ticket_event_notification_type_not_supported_error_message_without_event_type(self):
        error = TicketEventNotificationTypeNotSupportedError(
            None,
            NotificationTypeChoices.SMS
        )
        assert 'Notification type not supported' in str(error)

    def test_helpdesk_notification_recipient_missing_email_error_is_value_error(self):
        assert issubclass(HelpDeskNotificationRecipientMissingEmailError, ValueError)

    def test_helpdesk_notification_recipient_missing_email_error_message(self):
        error = HelpDeskNotificationRecipientMissingEmailError('John Doe')
        assert 'John Doe' in str(error)
        assert 'missing an email address' in str(error)
