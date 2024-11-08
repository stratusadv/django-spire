from django.apps import AppConfig


class PaginationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'example_pagination'
    name = 'example.pagination'
