from django.apps import AppConfig


class MfaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.user_account.authentication.mfa'
    label = 'authentication_mfa'
