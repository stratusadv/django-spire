from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.choices import (
    NotificationStatusChoices,
    NotificationTypeChoices,
)
from django_spire.notification.exceptions import NotificationError
from django_spire.notification.models import Notification
from django_spire.notification.sms.processor import SMSNotificationProcessor
from django_spire.notification.sms.tests.factories import create_test_sms_notification


class SMSNotificationProcessorTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = create_user(username='test_sms_processor_user')
        self.processor = SMSNotificationProcessor()

    @patch('django_spire.notification.sms.processor.Client')
    @patch('django_spire.notification.sms.processor.TwilioSMSHelper')
    def test_process_sets_status_to_sent(
        self,
        mock_helper_class: MagicMock,
        mock_client_class: MagicMock
    ):
        mock_helper = MagicMock()
        mock_helper_class.return_value = mock_helper

        sms_notification = create_test_sms_notification(user=self.user)
        notification = sms_notification.notification

        self.processor.process(notification)

        notification.refresh_from_db()
        assert notification.status == NotificationStatusChoices.SENT

    @patch('django_spire.notification.sms.processor.Client')
    @patch('django_spire.notification.sms.processor.TwilioSMSHelper')
    def test_process_sets_sent_datetime(
        self,
        mock_helper_class: MagicMock,
        mock_client_class: MagicMock
    ):
        mock_helper = MagicMock()
        mock_helper_class.return_value = mock_helper

        sms_notification = create_test_sms_notification(user=self.user)
        notification = sms_notification.notification

        self.processor.process(notification)

        notification.refresh_from_db()
        assert notification.sent_datetime is not None

    @patch('django_spire.notification.sms.processor.Client')
    @patch('django_spire.notification.sms.processor.TwilioSMSHelper')
    def test_process_calls_send(
        self,
        mock_helper_class: MagicMock,
        mock_client_class: MagicMock
    ):
        mock_helper = MagicMock()
        mock_helper_class.return_value = mock_helper

        sms_notification = create_test_sms_notification(user=self.user)
        notification = sms_notification.notification

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

    @patch('django_spire.notification.sms.processor.Client')
    @patch('django_spire.notification.sms.processor.BulkTwilioSMSHelper')
    def test_process_list(
        self,
        mock_helper_class: MagicMock,
        mock_client_class: MagicMock
    ):
        mock_helper = MagicMock()
        mock_helper_class.return_value = mock_helper

        notifications = [
            create_test_sms_notification(user=self.user).notification
            for _ in range(3)
        ]

        self.processor.process_list(notifications)

        mock_helper.send_notifications.assert_called_once()
