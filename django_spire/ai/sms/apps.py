from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class SmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.ai.sms'
    label = 'django_spire_ai_sms'

    REQUIRED_APPS = ('django_spire_ai', 'django_spire_ai_context')

    def ready(self):
        check_required_apps(self.label)
