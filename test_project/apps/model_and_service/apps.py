from django.apps import AppConfig


class ModelAndServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'test_project_model_and_service'
    name = 'test_project.apps.model_and_service'
