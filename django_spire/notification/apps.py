from django.apps import AppConfig

from django_spire.utils import check_required_apps


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.notification'
    label = 'django_spire_notification'
    
    REQUIRED_APPS = ('django_spire_core', 'django_spire_history', 'django_spire_history_viewed')

    def ready(self) -> None:
        check_required_apps(self.label)
