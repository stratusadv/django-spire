from django.apps import AppConfig


class DbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'spire_db'
    name = 'django_spire.db'
