from __future__ import annotations

from django.apps import AppConfig

from django_spire.tools import check_required_apps


class DomainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_metric_domain'
    name = 'django_spire.metric.domain'
    verbose_name = 'DJANGO_SPIRE_METRIC_DOMAIN'

    API_V1_ROUTER = 'django_spire.metric.domain.api_v1.router'
    API_V1_ROUTER_PREFIX = 'metric/domain'

    MODEL_PERMISSIONS = (
        {
            'name': 'metric_domain',
            'verbose_name': 'Metric Domain',
            'model_class_path': 'django_spire.metric.domain.models.Domain',
            'is_proxy_model': False,
        },
        {
            'name': 'metric_statistic',
            'verbose_name': 'Metric Statistic',
            'model_class_path': 'django_spire.metric.domain.statistic.models.Statistic',
            'is_proxy_model': False,
        },
    )

    REQUIRED_APPS = ('django_spire_core',)

    def ready(self) -> None:
        check_required_apps(self.label)
