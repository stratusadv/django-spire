from django.apps import AppConfig


class TaskConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'test_project.app.task'
    label = 'test_project_task'

    API_V1_ROUTER = 'test_project.app.task.api_v1.router'
    API_V1_ROUTER_PREFIX = 'task'
