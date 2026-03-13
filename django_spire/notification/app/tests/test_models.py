from __future__ import annotations

from django.utils.timezone import now, timedelta

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.app.tests.factories import create_test_app_notification
from django_spire.notification.models import Notification


class AppNotificationModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app_notification = create_test_app_notification()

    def test_str(self):
        assert str(self.app_notification) == self.app_notification.notification.title

    def test_verbose_time_since_delivered_just_now(self):
        self.app_notification.notification.sent_datetime = now()
        self.app_notification.notification.save()

        assert self.app_notification.verbose_time_since_delivered == 'just now'

    def test_verbose_time_since_delivered_minutes(self):
        self.app_notification.notification.sent_datetime = now() - timedelta(minutes=5)
        self.app_notification.notification.save()

        assert '5 minutes ago' in self.app_notification.verbose_time_since_delivered

    def test_verbose_time_since_delivered_hours(self):
        self.app_notification.notification.sent_datetime = now() - timedelta(hours=3)
        self.app_notification.notification.save()

        assert '3 hours ago' in self.app_notification.verbose_time_since_delivered

    def test_verbose_time_since_delivered_days(self):
        self.app_notification.notification.sent_datetime = now() - timedelta(days=2)
        self.app_notification.notification.save()

        assert '2 days ago' in self.app_notification.verbose_time_since_delivered

    def test_verbose_time_since_delivered_singular_day(self):
        self.app_notification.notification.sent_datetime = now() - timedelta(days=1)
        self.app_notification.notification.save()

        assert '1 day ago' in self.app_notification.verbose_time_since_delivered

    def test_as_dict(self):
        result = self.app_notification.as_dict()

        assert result['id'] == self.app_notification.id
        assert result['title'] == self.app_notification.notification.title
        assert result['body'] == self.app_notification.notification.body
        assert result['url'] == self.app_notification.notification.url
        assert result['priority'] == self.app_notification.notification.priority
        assert 'time_since_delivered' in result
        assert 'context_data' in result

    def test_as_json(self):
        result = self.app_notification.as_json()
        assert isinstance(result, str)
        assert self.app_notification.notification.title in result

    def test_notification_relationship(self):
        assert self.app_notification.notification is not None
        assert isinstance(self.app_notification.notification, Notification)

    def test_default_template(self):
        assert self.app_notification.template == 'django_spire/notification/app/item/notification_item.html'

    def test_default_context_data(self):
        assert self.app_notification.context_data == {}
