from __future__ import annotations

from django.apps import apps

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.email.apps import NotificationEmailConfig


class NotificationEmailConfigTests(BaseTestCase):
    def test_app_name(self):
        assert NotificationEmailConfig.name == 'django_spire.notification.email'

    def test_app_label(self):
        assert NotificationEmailConfig.label == 'django_spire_notification_email'

    def test_default_auto_field(self):
        assert NotificationEmailConfig.default_auto_field == 'django.db.models.BigAutoField'

    def test_required_apps(self):
        expected = ('django_spire_core', 'django_spire_notification')
        assert NotificationEmailConfig.REQUIRED_APPS == expected

    def test_app_is_installed(self):
        assert apps.is_installed('django_spire.notification.email')
