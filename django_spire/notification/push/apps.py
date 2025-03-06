from django.apps import AppConfig


class NotificationPushConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.notification.push'
    label = 'spire_notification_push'
