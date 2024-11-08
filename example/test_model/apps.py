from django.apps import AppConfig


class TestModelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'example_test_model'
    name = 'example.test_model'
