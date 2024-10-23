from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.user_account.authentication'
    label = 'user_account_authentication'
