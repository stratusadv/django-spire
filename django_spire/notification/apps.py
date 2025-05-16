from django.apps import AppConfig
from django.conf import settings

from django_spire.consts import NOTIFICATION_THROTTLE_RATE_PER_MINUTE_SETTINGS_NAME
from django_spire.utils import check_required_apps


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.notification'
    label = 'django_spire_notification'

    REQUIRED_APPS = ('django_spire_core', 'django_spire_history', 'django_spire_history_viewed')

    URLPATTERNS_INCLUDE = 'django_spire.notification.urls'
    URLPATTERNS_NAMESPACE = 'notification'

    def ready(self) -> None:
        if not isinstance(getattr(settings, NOTIFICATION_THROTTLE_RATE_PER_MINUTE_SETTINGS_NAME), int):
            raise ValueError(f'"{NOTIFICATION_THROTTLE_RATE_PER_MINUTE_SETTINGS_NAME}" must be set in the django settings when using "{self.label}".')

        check_required_apps(self.label)
