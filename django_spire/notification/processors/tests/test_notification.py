from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.app.models import AppNotification
from django_spire.notification.choices import (
    NotificationStatusChoices,
    NotificationTypeChoices,
)
from django_spire.notification.exceptions import NotificationError
from django_spire.notification.models import Notification
from django_spire.notification.processors.notification import NotificationProcessor


class NotificationProcessorTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.user = create_user(username='test_processor_user')
        self.processor = NotificationProcessor()

    def _create_notification(self, **kwargs) -> Notification:
        data = {
            'user': self.user,
            'type': NotificationTypeChoices.APP,
            'title': 'Test Notification',
            'body': 'Test body',
            'status': NotificationStatusChoices.PENDING,
        }
        data.update(kwargs)
        notification = Notification.objects.create(**data)

        if data['type'] == NotificationTypeChoices.APP:
            AppNotification.objects.create(notification=notification)

        return notification

    @patch('django_spire.notification.processors.notification.AppNotificationProcessor')
    def test_process_app_notification(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        notification = self._create_notification(type=NotificationTypeChoices.APP)

        self.processor.process(notification)

        mock_processor.process.assert_called_once_with(notification)

    @patch('django_spire.notification.processors.notification.EmailNotificationProcessor')
    def test_process_email_notification(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        notification = self._create_notification(type=NotificationTypeChoices.EMAIL)

        self.processor.process(notification)

        mock_processor.process.assert_called_once_with(notification)

    @patch('django_spire.notification.processors.notification.SMSNotificationProcessor')
    def test_process_sms_notification(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        notification = self._create_notification(type=NotificationTypeChoices.SMS)

        self.processor.process(notification)

        mock_processor.process.assert_called_once_with(notification)

    def test_process_unknown_type_raises_error(self):
        notification = self._create_notification()
        notification.type = 'unknown'

        with pytest.raises(NotificationError):
            self.processor.process(notification)

    def test_process_unknown_type_sets_status_failed(self):
        notification = self._create_notification()
        notification.type = 'unknown'

        with pytest.raises(NotificationError):
            self.processor.process(notification)

        notification.refresh_from_db()
        assert notification.status == NotificationStatusChoices.FAILED

    @patch('django_spire.notification.processors.notification.AppNotificationProcessor')
    def test_process_list_groups_by_type(self, mock_processor_class: MagicMock):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        notifications = [
            self._create_notification(type=NotificationTypeChoices.APP),
            self._create_notification(type=NotificationTypeChoices.APP),
        ]

        self.processor.process_list(notifications)

        mock_processor.process_list.assert_called_once()
        call_args = mock_processor.process_list.call_args[0][0]
        assert len(call_args) == 2
