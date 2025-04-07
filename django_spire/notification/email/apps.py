from django.apps import AppConfig


class NotificationEmailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.notification.email'
    label = 'spire_notification_email'
