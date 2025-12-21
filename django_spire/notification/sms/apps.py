from __future__ import annotations

from django.apps import AppConfig
from django.conf import settings

from django_spire.notification.sms.consts import TWILIO_SMS_BATCH_SIZE_NAME
from django_spire.utils import check_required_apps


class NotificationSmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.notification.sms'
    label = 'django_spire_notification_sms'

    REQUIRED_APPS = ('django_spire_core', 'django_spire_notification')

    def ready(self) -> None:
        if not isinstance(getattr(settings, TWILIO_SMS_BATCH_SIZE_NAME), int):
            message = f'"{TWILIO_SMS_BATCH_SIZE_NAME}" must be set in the django settings when using "{self.label}".'
            raise TypeError(message)

        check_required_apps(self.label)
