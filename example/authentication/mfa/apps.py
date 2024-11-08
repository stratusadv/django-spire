from django.apps import AppConfig


class AuthenticationMfaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'example_authentication_mfa'
    name = 'example.authentication.mfa'
