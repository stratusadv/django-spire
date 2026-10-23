from django.apps import AppConfig


class CeleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'test_project_celery'
    name = 'test_project.app.celery'

    API_V1_ROUTER = 'test_project.app.celery.api_v1.router'
    API_V1_ROUTER_PREFIX = 'celery'
