from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_ai'
    name = 'django_spire.ai'

    REQUIRED_APPS = ('django_spire_core',)
    URLPATTERNS_INCLUDE = 'django_spire.ai.urls'
    URLPATTERNS_NAMESPACE = 'ai'

    def ready(self) -> None:
        check_required_apps(self.label)
