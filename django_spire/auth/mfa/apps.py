from django.apps import AppConfig

from django_spire.utils import check_required_apps


class MfaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_auth_mfa'
    name = 'django_spire.auth.mfa'


    REQUIRED_APPS = ('django_spire_core', 'django_spire_auth')

    def ready(self) -> None:
        check_required_apps(self.label)
