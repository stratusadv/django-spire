from django.apps import AppConfig


class DummyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'testing.dummy'
    label = 'dummy'
