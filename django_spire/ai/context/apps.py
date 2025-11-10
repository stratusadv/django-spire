from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class AiContextConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.ai.context'
    label = 'django_spire_ai_context'

    REQUIRED_APPS = ('django_spire_ai',)

    def ready(self) -> None:
        check_required_apps(self.label)
