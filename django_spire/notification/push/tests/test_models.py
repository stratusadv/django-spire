from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.push.models import PushNotification


class PushNotificationModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.push_notification = PushNotification.objects.create()

    def test_created_datetime_auto_set(self):
        assert self.push_notification.created_datetime is not None

    def test_is_active_default_true(self):
        assert self.push_notification.is_active is True

    def test_is_deleted_default_false(self):
        assert self.push_notification.is_deleted is False

    def test_meta_verbose_name(self):
        assert PushNotification._meta.verbose_name == 'Push Notification'

    def test_meta_verbose_name_plural(self):
        assert PushNotification._meta.verbose_name_plural == 'Push Notifications'

    def test_meta_db_table(self):
        assert PushNotification._meta.db_table == 'django_spire_notification_push'
