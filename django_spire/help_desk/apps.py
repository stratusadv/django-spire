from django.apps import AppConfig

from django_spire.utils import check_required_apps


class HelpDeskConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_help_desk'
    name = 'django_spire.help_desk'

    REQUIRED_APPS = ('django_spire_core',)

    def ready(self) -> None:
        check_required_apps(self.label)
