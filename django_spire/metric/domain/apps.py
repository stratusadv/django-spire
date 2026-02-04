from __future__ import annotations

from django.apps import AppConfig


class DomainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'metric_domain'
    name = 'django_spire.metric.domain'

    MODEL_PERMISSIONS = (
        {
            'name': 'metric_domain',
            'model_class_path': 'django_spire.metric.domain.models.Domain',
            'is_proxy_model': False
        },
    )
