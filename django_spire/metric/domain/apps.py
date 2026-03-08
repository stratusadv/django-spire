from __future__ import annotations

from django.apps import AppConfig


class DomainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'metric_domain'
    name = 'django_spire.metric.domain'

    URLPATTERNS_NAMESPACE = 'domain'
    URLPATTERNS_API_V1 = 'django_spire.metric.domain.api_v1'
    URLPATTERNS_API_V1_PREFIX = 'metric/domain'

    MODEL_PERMISSIONS = (
        {
            'name': 'metric_domain',
            'model_class_path': 'django_spire.metric.domain.models.Domain',
            'is_proxy_model': False
        },
    )
