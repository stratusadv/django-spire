from django.apps import AppConfig


class SmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.ai.sms'
    verbose_name = 'SMS'

    REQUIRED_APPS = ('django_spire_ai',)

    def ready(self):
        pass  # Import signals or perform other initialization here if needed