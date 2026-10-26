from django.apps import AppConfig


class MetricsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'test_project_metrics'
    name = 'test_project.app.metrics'
