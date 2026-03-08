from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_api'
    name = 'django_spire.api'
    MODEL_PERMISSIONS = (
        {
            'name': 'api',
            'verbose_name': 'Api',
            'model_class_path': 'django_spire.api.models.ApiAccess',
            'is_proxy_model': False,
        },
    )

    REQUIRED_APPS = ('django_spire_core',)

    URLPATTERNS_INCLUDE = 'django_spire.api.urls'
    URLPATTERNS_NAMESPACE = 'api'

    def ready(self) -> None:
        check_required_apps(self.label)
