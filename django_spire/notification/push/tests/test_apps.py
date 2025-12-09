from __future__ import annotations

from django.apps import apps

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.push.apps import NotificationPushConfig


class NotificationPushConfigTests(BaseTestCase):
    def test_app_name(self):
        assert NotificationPushConfig.name == 'django_spire.notification.push'

    def test_app_label(self):
        assert NotificationPushConfig.label == 'django_spire_notification_push'

    def test_default_auto_field(self):
        assert NotificationPushConfig.default_auto_field == 'django.db.models.BigAutoField'

    def test_required_apps(self):
        expected = ('django_spire_core', 'django_spire_notification')
        assert NotificationPushConfig.REQUIRED_APPS == expected

    def test_app_is_installed(self):
        assert apps.is_installed('django_spire.notification.push')
