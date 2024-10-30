from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'spire_permission'
    name = 'django_spire.core'
