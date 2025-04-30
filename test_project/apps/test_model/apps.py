from django.apps import AppConfig


class TestModelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'test_project_test_model'
    name = 'test_project.apps.test_model'
