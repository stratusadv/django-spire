from django.apps import AppConfig
from django.conf import settings
from django_spire.tools import check_required_apps

class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.notification'
    label = 'spire_notification'
    REQUIRED_APPS = ('spire_core', 'spire_history', 'spire_history_viewed')

    def ready(self) -> None:
        # Dynamically add sub-apps to INSTALLED_APPS
        settings.INSTALLED_APPS += [
            'django_spire.notification.app',
            'django_spire.notification.email',
            # 'django_spire.notification.push',
            # 'dj
        ]
        check_required_apps(self.label)
