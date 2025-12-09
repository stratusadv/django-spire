from __future__ import annotations

import pytest

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.app.exceptions import AppNotificationError
from django_spire.notification.app.models import AppNotification
from django_spire.notification.app.processor import AppNotificationProcessor
from django_spire.notification.choices import (
    NotificationStatusChoices,
    NotificationTypeChoices,
)
from django_spire.notification.exceptions import NotificationError
from django_spire.notification.models import Notification


class AppNotificationProcessorTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = create_user(username='test_processor_user')
        self.processor = AppNotificationProcessor()

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
        AppNotification.objects.create(notification=notification)
        return notification

    def test_process_sets_status_to_sent(self):
        notification = self._create_notification()

        self.processor.process(notification)

        notification.refresh_from_db()
        assert notification.status == NotificationStatusChoices.SENT

    def test_process_sets_sent_datetime(self):
        notification = self._create_notification()

        self.processor.process(notification)

        notification.refresh_from_db()
        assert notification.sent_datetime is not None

    def test_process_raises_error_for_wrong_type(self):
        notification = self._create_notification(type=NotificationTypeChoices.EMAIL)

        with pytest.raises(NotificationError):
            self.processor.process(notification)

    def test_process_raises_error_for_missing_user(self):
        notification = Notification.objects.create(
            user=None,
            type=NotificationTypeChoices.APP,
            title='Test',
            body='Test',
            status=NotificationStatusChoices.PENDING,
        )
        AppNotification.objects.create(notification=notification)

        with pytest.raises(AppNotificationError):
            self.processor.process(notification)

    def test_process_list(self):
        notifications = [self._create_notification() for _ in range(3)]

        self.processor.process_list(notifications)

        for notification in notifications:
            notification.refresh_from_db()
            assert notification.status == NotificationStatusChoices.SENT
            assert notification.sent_datetime is not None

    def test_process_list_raises_error_for_wrong_type(self):
        notifications = [
            self._create_notification(),
            self._create_notification(type=NotificationTypeChoices.EMAIL),
        ]

        with pytest.raises(NotificationError):
            self.processor.process_list(notifications)

    def test_process_ready(self):
        pending_notification = self._create_notification()

        sent_notification = self._create_notification(
            status=NotificationStatusChoices.SENT
        )

        self.processor.process_ready()

        pending_notification.refresh_from_db()
        assert pending_notification.status == NotificationStatusChoices.SENT

    def test_process_errored(self):
        errored_notification = self._create_notification(
            status=NotificationStatusChoices.ERRORED
        )

        self.processor.process_errored()

        errored_notification.refresh_from_db()
        assert errored_notification.status == NotificationStatusChoices.SENT
