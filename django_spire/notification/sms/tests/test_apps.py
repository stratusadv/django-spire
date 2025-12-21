from __future__ import annotations

from django.apps import apps

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.sms.apps import NotificationSmsConfig


class NotificationSmsConfigTests(BaseTestCase):
    def test_app_name(self):
        assert NotificationSmsConfig.name == 'django_spire.notification.sms'

    def test_app_label(self):
        assert NotificationSmsConfig.label == 'django_spire_notification_sms'

    def test_default_auto_field(self):
        assert NotificationSmsConfig.default_auto_field == 'django.db.models.BigAutoField'

    def test_required_apps(self):
        expected = ('django_spire_core', 'django_spire_notification')
        assert expected == NotificationSmsConfig.REQUIRED_APPS

    def test_app_is_installed(self):
        assert apps.is_installed('django_spire.notification.sms')
