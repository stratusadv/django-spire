from django.apps import AppConfig


class MfaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'spire_authentication_mfa'
    name = 'django_spire.authentication.mfa'
