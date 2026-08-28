from __future__ import annotations

from django.apps import AppConfig

from django_spire.tools import check_required_apps


class VisualConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_metric_visual'
    name = 'django_spire.metric.visual'
    verbose_name = 'DJANGO_SPIRE_METRIC_VISUAL'

    MODEL_PERMISSIONS = (
        {
            'name': 'metric_visual',
            'verbose_name': 'Metric Visual',
            'model_class_path': 'django_spire.metric.visual.models.Visual',
            'is_proxy_model': False,
        },
    )

    REQUIRED_APPS = ('django_spire_core', 'django_spire_metric_domain')

    def ready(self) -> None:
        check_required_apps(self.label)
