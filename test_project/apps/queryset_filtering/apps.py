from django.apps import AppConfig


class QuerySetFilteringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'test_project.apps.queryset_filtering'
    label = 'test_project_queryset_filtering'

    API_V1_ROUTER = 'test_project.apps.queryset_filtering.api_v1.router'
    API_V1_ROUTER_PREFIX = 'task'
