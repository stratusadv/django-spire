from __future__ import annotations

from django.apps import apps

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.app.apps import NotificationAppConfig


class NotificationAppConfigTests(BaseTestCase):
    def test_app_name(self):
        assert NotificationAppConfig.name == 'django_spire.notification.app'

    def test_app_label(self):
        assert NotificationAppConfig.label == 'django_spire_notification_app'

    def test_default_auto_field(self):
        assert NotificationAppConfig.default_auto_field == 'django.db.models.BigAutoField'

    def test_required_apps(self):
        expected = ('django_spire_core', 'django_spire_notification')
        assert expected == NotificationAppConfig.REQUIRED_APPS

    def test_app_is_installed(self):
        assert apps.is_installed('django_spire.notification.app')
