from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.history.viewed.models import Viewed
from django_spire.notification.app.models import AppNotification
from django_spire.notification.app.tests.factories import create_test_app_notification
from django_spire.notification.choices import NotificationStatusChoices


class AppNotificationQuerySetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = create_user(username='test_app_notification_user')
        self.app_notification = create_test_app_notification(user=self.user)

    def _create_viewed_for_notification(self, app_notification: AppNotification, user):
        content_type = ContentType.objects.get_for_model(AppNotification)
        Viewed.objects.create(
            user=user,
            object_id=app_notification.id,
            content_type=content_type
        )

    def test_by_user(self):
        other_user = create_user(username='other_user')
        other_notification = create_test_app_notification(user=other_user)

        result = AppNotification.objects.by_user(self.user)
        assert self.app_notification in result
        assert other_notification not in result

    def test_by_users(self):
        other_user = create_user(username='other_user')
        other_notification = create_test_app_notification(user=other_user)

        result = AppNotification.objects.by_users([self.user, other_user])
        assert self.app_notification in result
        assert other_notification in result

    def test_is_sent(self):
        pending_notification = create_test_app_notification(
            user=self.user,
            status=NotificationStatusChoices.PENDING
        )

        result = AppNotification.objects.is_sent()
        assert self.app_notification in result
        assert pending_notification not in result

    def test_exclude_viewed_by_user(self):
        self._create_viewed_for_notification(self.app_notification, self.user)

        result = AppNotification.objects.exclude_viewed_by_user(self.user)
        assert self.app_notification not in result

    def test_annotate_is_viewed_by_user_false(self):
        result = AppNotification.objects.annotate_is_viewed_by_user(self.user).first()
        assert result.viewed is False

    def test_annotate_is_viewed_by_user_true(self):
        self._create_viewed_for_notification(self.app_notification, self.user)

        result = AppNotification.objects.annotate_is_viewed_by_user(self.user).first()
        assert result.viewed is True

    def test_ordered_by_priority_and_sent_datetime(self):
        same_time = now()
        high_priority = create_test_app_notification(
            user=self.user,
            priority='high',
            sent_datetime=same_time
        )
        low_priority = create_test_app_notification(
            user=self.user,
            priority='low',
            sent_datetime=same_time
        )

        result = list(
            AppNotification.objects
            .filter(pk__in=[high_priority.pk, low_priority.pk])
            .ordered_by_priority_and_sent_datetime()
        )

        assert result[0].pk == high_priority.pk
        assert result[1].pk == low_priority.pk
