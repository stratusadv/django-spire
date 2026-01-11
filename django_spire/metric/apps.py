from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class MetricConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'metric'
    name = 'django_spire.metric'

    REQUIRED_APPS = ('django_spire_core',)

    URLPATTERNS_INCLUDE = 'django_spire.metric.urls'
    URLPATTERNS_NAMESPACE = 'metric'

    def ready(self) -> None:
        check_required_apps(self.label)
