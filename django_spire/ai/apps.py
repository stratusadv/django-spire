from django.apps import AppConfig
from django.conf import settings

from django_spire.tools import check_required_apps


class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.ai'
    label = 'spire_ai'
    REQUIRED_APPS = ('spire_core',)

    def ready(self) -> None:
        settings.INSTALLED_APPS += [
            'django_spire.ai.chat',
        ]
        check_required_apps(self.label)
