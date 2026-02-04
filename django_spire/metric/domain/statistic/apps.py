from __future__ import annotations

from django.apps import AppConfig


class StatisticConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'domain_statistic'
    name = 'django_spire.metric.domain.statistic'

    MODEL_PERMISSIONS = (
        {
            'name': 'domain_statistic',
            'model_class_path': 'django_spire.metric.domain.statistic.models.Statistic',
            'is_proxy_model': False
        },
    )
