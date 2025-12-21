from __future__ import annotations

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.choices import NotificationStatusChoices
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.email.tests.factories import create_test_email_notification


class EmailNotificationQuerySetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = create_user(username='test_email_queryset_user')
        self.email_notification = create_test_email_notification(
            user=self.user,
            status=NotificationStatusChoices.SENT
        )

    def test_by_user(self):
        other_user = create_user(username='other_user')
        other_notification = create_test_email_notification(user=other_user)

        result = EmailNotification.objects.by_user(self.user)
        assert self.email_notification in result
        assert other_notification not in result

    def test_by_users(self):
        other_user = create_user(username='other_user')
        other_notification = create_test_email_notification(user=other_user)

        result = EmailNotification.objects.by_users([self.user, other_user])
        assert self.email_notification in result
        assert other_notification in result

    def test_is_sent(self):
        pending_notification = create_test_email_notification(
            user=self.user,
            status=NotificationStatusChoices.PENDING
        )

        result = EmailNotification.objects.is_sent()
        assert self.email_notification in result
        assert pending_notification not in result
