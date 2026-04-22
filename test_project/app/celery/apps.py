from django.apps import AppConfig


class CeleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'test_project_celery'
    name = 'test_project.app.celery'
