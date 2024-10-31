from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'spire_authentication'
    name = 'django_spire.authentication'
