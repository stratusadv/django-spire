from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class CeleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_celery'
    name = 'django_spire.celery'
    MODEL_PERMISSIONS = (
        {
            'name': 'celery',
            'verbose_name': 'Celery',
            'model_class_path': 'django_spire.celery.models.CeleryTask',
            'is_proxy_model': False,
        },
    )

    REQUIRED_APPS = ('django_spire_core',)

    URLPATTERNS_INCLUDE = 'django_spire.celery.urls'
    URLPATTERNS_NAMESPACE = 'celery'

    def ready(self) -> None:
        check_required_apps(self.label)
