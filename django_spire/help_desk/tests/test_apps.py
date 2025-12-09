from __future__ import annotations

from django.apps import apps

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.apps import HelpDeskConfig


class HelpDeskConfigTests(BaseTestCase):
    def test_app_name(self):
        assert HelpDeskConfig.name == 'django_spire.help_desk'

    def test_app_label(self):
        assert HelpDeskConfig.label == 'django_spire_help_desk'

    def test_default_auto_field(self):
        assert HelpDeskConfig.default_auto_field == 'django.db.models.BigAutoField'

    def test_required_apps(self):
        assert HelpDeskConfig.REQUIRED_APPS == ('django_spire_core',)

    def test_urlpatterns_include(self):
        assert HelpDeskConfig.URLPATTERNS_INCLUDE == 'django_spire.help_desk.urls'

    def test_urlpatterns_namespace(self):
        assert HelpDeskConfig.URLPATTERNS_NAMESPACE == 'help_desk'

    def test_model_permissions(self):
        expected = (
            {
                'name': 'help_desk',
                'verbose_name': 'Help Desk',
                'model_class_path': 'django_spire.help_desk.models.HelpDeskTicket',
                'is_proxy_model': False,
            },
        )

        assert expected == HelpDeskConfig.MODEL_PERMISSIONS

    def test_app_is_installed(self):
        assert apps.is_installed('django_spire.help_desk')
