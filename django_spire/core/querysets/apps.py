from django.apps import AppConfig

from django_spire.utils import check_required_apps


class QuerySetAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.core.querysets'
    label = 'django_spire_core_queryset'
