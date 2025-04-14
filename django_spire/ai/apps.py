from django.apps import AppConfig

from django_spire.tools import check_required_apps


class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.ai'
    label = 'spire_ai'
    REQUIRED_APPS = ('spire_core',)

    def ready(self) -> None:
        check_required_apps(self.label)
