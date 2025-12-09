from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.choices import (
    NotificationStatusChoices,
    NotificationTypeChoices,
)
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.email.processor import EmailNotificationProcessor
from django_spire.notification.email.tests.factories import create_test_email_notification
from django_spire.notification.exceptions import NotificationError
from django_spire.notification.models import Notification


class EmailNotificationProcessorTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = create_user(username='test_email_processor_user')
        self.processor = EmailNotificationProcessor()

    @patch('django_spire.notification.email.processor.SendGridEmailHelper')
    def test_process_sets_status_to_sent(self, mock_helper_class: MagicMock):
        mock_helper = MagicMock()
        mock_helper_class.return_value = mock_helper

        email_notification = create_test_email_notification(user=self.user)
        notification = email_notification.notification

        self.processor.process(notification)

        notification.refresh_from_db()
        assert notification.status == NotificationStatusChoices.SENT

    @patch('django_spire.notification.email.processor.SendGridEmailHelper')
    def test_process_sets_sent_datetime(self, mock_helper_class: MagicMock):
        mock_helper = MagicMock()
        mock_helper_class.return_value = mock_helper

        email_notification = create_test_email_notification(user=self.user)
        notification = email_notification.notification

        self.processor.process(notification)

        notification.refresh_from_db()
        assert notification.sent_datetime is not None

    @patch('django_spire.notification.email.processor.SendGridEmailHelper')
    def test_process_calls_send(self, mock_helper_class: MagicMock):
        mock_helper = MagicMock()
        mock_helper_class.return_value = mock_helper

        email_notification = create_test_email_notification(user=self.user)
        notification = email_notification.notification

        self.processor.process(notification)

        mock_helper.send.assert_called_once()

    def test_process_raises_error_for_wrong_type(self):
        notification = Notification.objects.create(
            user=self.user,
            type=NotificationTypeChoices.APP,
            title='Test',
            body='Test',
            status=NotificationStatusChoices.PENDING,
        )

        with pytest.raises(NotificationError):
            self.processor.process(notification)

    @patch('django_spire.notification.email.processor.SendGridEmailHelper')
    def test_process_list(self, mock_helper_class: MagicMock):
        mock_helper = MagicMock()
        mock_helper_class.return_value = mock_helper

        notifications = [
            create_test_email_notification(user=self.user).notification
            for _ in range(3)
        ]

        self.processor.process_list(notifications)

        for notification in notifications:
            notification.refresh_from_db()
            assert notification.status == NotificationStatusChoices.SENT

        assert mock_helper.send.call_count == 3
