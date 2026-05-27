from __future__ import annotations

from django.apps import AppConfig
from django_spire.conf import settings

from django_spire.tools import check_required_apps


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.notification'
    label = 'django_spire_notification'

    REQUIRED_APPS = ('django_spire_core', 'django_spire_history', 'django_spire_history_viewed')

    URLPATTERNS_INCLUDE = 'django_spire.notification.urls'
    URLPATTERNS_NAMESPACE = 'notification'

    def ready(self) -> None:
        if not isinstance(settings.DJANGO_SPIRE_NOTIFICATION_THROTTLE_RATE_PER_MINUTE, int):
            message = '"DJANGO_SPIRE_NOTIFICATION_THROTTLE_RATE_PER_MINUTE" must be set in the django settings when using "{self.label}".'
            raise TypeError(message)

        check_required_apps(self.label)
