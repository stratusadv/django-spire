from django.apps import AppConfig

from django_spire.utils import check_required_apps


class SmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.ai.sms'
    verbose_name = 'SMS'

    REQUIRED_APPS = ('django_spire_ai',)

    def ready(self):
        check_required_apps(self.label)
