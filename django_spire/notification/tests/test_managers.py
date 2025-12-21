from __future__ import annotations

from unittest.mock import MagicMock, patch

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.managers import NotificationManager


class NotificationManagerTests(BaseTestCase):
    @patch('django_spire.notification.managers.NotificationProcessor')
    def test_process_ready_notifications(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        NotificationManager.process_ready_notifications()

        mock_processor.process_ready.assert_called_once()

    @patch('django_spire.notification.managers.NotificationProcessor')
    def test_process_errored_notifications(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        NotificationManager.process_errored_notifications()

        mock_processor.process_errored.assert_called_once()

    @patch('django_spire.notification.managers.AppNotificationProcessor')
    def test_process_ready_app_notifications(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        NotificationManager.process_ready_app_notifications()

        mock_processor.process_ready.assert_called_once()

    @patch('django_spire.notification.managers.AppNotificationProcessor')
    def test_process_errored_app_notifications(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        NotificationManager.process_errored_app_notifications()

        mock_processor.process_errored.assert_called_once()

    @patch('django_spire.notification.managers.EmailNotificationProcessor')
    def test_process_ready_email_notifications(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        NotificationManager.process_ready_email_notifications()

        mock_processor.process_ready.assert_called_once()

    @patch('django_spire.notification.managers.EmailNotificationProcessor')
    def test_process_errored_email_notifications(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        NotificationManager.process_errored_email_notifications()

        mock_processor.process_errored.assert_called_once()

    @patch('django_spire.notification.managers.SMSNotificationProcessor')
    def test_process_ready_sms_notifications(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        NotificationManager.process_ready_sms_notifications()

        mock_processor.process_ready.assert_called_once()

    @patch('django_spire.notification.managers.SMSNotificationProcessor')
    def test_process_errored_sms_notifications(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        NotificationManager.process_errored_sms_notifications()

        mock_processor.process_errored.assert_called_once()

    @patch('django_spire.notification.managers.NotificationProcessor')
    def test_process_notification(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_notification = MagicMock()

        NotificationManager.process_notification(mock_notification)

        mock_processor.process.assert_called_once_with(mock_notification)

    @patch('django_spire.notification.managers.NotificationProcessor')
    def test_process_notifications(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_notifications = [MagicMock(), MagicMock()]

        NotificationManager.process_notifications(mock_notifications)

        mock_processor.process_list.assert_called_once_with(mock_notifications)
