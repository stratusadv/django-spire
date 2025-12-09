from __future__ import annotations

from django.apps import apps

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.apps import NotificationConfig


class NotificationConfigTests(BaseTestCase):
    def test_app_name(self):
        assert NotificationConfig.name == 'django_spire.notification'

    def test_app_label(self):
        assert NotificationConfig.label == 'django_spire_notification'

    def test_default_auto_field(self):
        assert NotificationConfig.default_auto_field == 'django.db.models.BigAutoField'

    def test_required_apps(self):
        expected = ('django_spire_core', 'django_spire_history', 'django_spire_history_viewed')
        assert expected == NotificationConfig.REQUIRED_APPS

    def test_urlpatterns_include(self):
        assert NotificationConfig.URLPATTERNS_INCLUDE == 'django_spire.notification.urls'

    def test_urlpatterns_namespace(self):
        assert NotificationConfig.URLPATTERNS_NAMESPACE == 'notification'

    def test_app_is_installed(self):
        assert apps.is_installed('django_spire.notification')
