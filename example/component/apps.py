from django.apps import AppConfig


class ComponentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'component'
    name = 'example.component'

