from django.apps import AppConfig

from django_spire.utils import check_required_apps


class NotificationSmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.notification.sms'
    label = 'django_spire_notification_sms'

    REQUIRED_APPS = ('django_spire_core', 'django_spire_notification')

    def ready(self) -> None:
        check_required_apps(self.label)
