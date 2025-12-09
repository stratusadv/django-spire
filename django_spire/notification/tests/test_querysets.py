from __future__ import annotations

from django.utils.timezone import now, timedelta

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.choices import (
    NotificationPriorityChoices,
    NotificationStatusChoices,
    NotificationTypeChoices,
)
from django_spire.notification.models import Notification
from django_spire.notification.tests.factories import create_test_notification


class NotificationQuerySetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = create_user(username='test_notification_user')
        self.notification = create_test_notification(user=self.user)

    def test_active_returns_non_deleted(self):
        result = Notification.objects.active()
        assert self.notification in result

    def test_active_excludes_deleted(self):
        self.notification.is_deleted = True
        self.notification.save()

        result = Notification.objects.active()
        assert self.notification not in result

    def test_by_user(self):
        other_user = create_user(username='other_user')
        other_notification = create_test_notification(user=other_user)

        result = Notification.objects.by_user(self.user)
        assert self.notification in result
        assert other_notification not in result

    def test_by_users(self):
        other_user = create_user(username='other_user')
        other_notification = create_test_notification(user=other_user)

        result = Notification.objects.by_users([self.user, other_user])
        assert self.notification in result
        assert other_notification in result

    def test_app_notifications(self):
        self.notification.type = NotificationTypeChoices.APP
        self.notification.save()

        email_notification = create_test_notification(
            user=self.user,
            type=NotificationTypeChoices.EMAIL
        )

        result = Notification.objects.app_notifications()
        assert self.notification in result
        assert email_notification not in result

    def test_email_notifications(self):
        self.notification.type = NotificationTypeChoices.EMAIL
        self.notification.save()

        app_notification = create_test_notification(
            user=self.user,
            type=NotificationTypeChoices.APP
        )

        result = Notification.objects.email_notifications()
        assert self.notification in result
        assert app_notification not in result

    def test_sms_notifications(self):
        self.notification.type = NotificationTypeChoices.SMS
        self.notification.save()

        result = Notification.objects.sms_notifications()
        assert self.notification in result

    def test_pending(self):
        self.notification.status = NotificationStatusChoices.PENDING
        self.notification.save()

        sent_notification = create_test_notification(
            user=self.user,
            status=NotificationStatusChoices.SENT
        )

        result = Notification.objects.pending()
        assert self.notification in result
        assert sent_notification not in result

    def test_processing(self):
        self.notification.status = NotificationStatusChoices.PROCESSING
        self.notification.save()

        result = Notification.objects.processing()
        assert self.notification in result

    def test_sent(self):
        self.notification.status = NotificationStatusChoices.SENT
        self.notification.save()

        result = Notification.objects.sent()
        assert self.notification in result

    def test_errored(self):
        self.notification.status = NotificationStatusChoices.ERRORED
        self.notification.save()

        result = Notification.objects.errored()
        assert self.notification in result

    def test_failed(self):
        self.notification.status = NotificationStatusChoices.FAILED
        self.notification.save()

        result = Notification.objects.failed()
        assert self.notification in result

    def test_unsent(self):
        pending = create_test_notification(
            user=self.user,
            status=NotificationStatusChoices.PENDING
        )
        processing = create_test_notification(
            user=self.user,
            status=NotificationStatusChoices.PROCESSING
        )
        sent = create_test_notification(
            user=self.user,
            status=NotificationStatusChoices.SENT
        )

        result = Notification.objects.unsent()
        assert pending in result
        assert processing in result
        assert sent not in result

    def test_ready_to_send(self):
        past_notification = create_test_notification(
            user=self.user,
            status=NotificationStatusChoices.PENDING,
            publish_datetime=now() - timedelta(hours=1)
        )
        future_notification = create_test_notification(
            user=self.user,
            status=NotificationStatusChoices.PENDING,
            publish_datetime=now() + timedelta(hours=1)
        )

        result = Notification.objects.ready_to_send()
        assert past_notification in result
        assert future_notification not in result

    def test_high_priority(self):
        self.notification.priority = NotificationPriorityChoices.HIGH
        self.notification.save()

        low_priority = create_test_notification(
            user=self.user,
            priority=NotificationPriorityChoices.LOW
        )

        result = Notification.objects.high_priority()
        assert self.notification in result
        assert low_priority not in result

    def test_medium_priority(self):
        self.notification.priority = NotificationPriorityChoices.MEDIUM
        self.notification.save()

        result = Notification.objects.medium_priority()
        assert self.notification in result

    def test_low_priority(self):
        self.notification.priority = NotificationPriorityChoices.LOW
        self.notification.save()

        result = Notification.objects.low_priority()
        assert self.notification in result
