from __future__ import annotations

from django.apps import AppConfig

from django_spire.tools import check_required_apps


class AuthSmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.auth.sms'
    label = 'django_spire_auth_sms'

    REQUIRED_APPS = ('django_spire_core', 'django_spire_auth')

    def ready(self) -> None:
        check_required_apps(self.label)
