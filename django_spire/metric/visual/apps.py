from __future__ import annotations

from django.apps import AppConfig


class VisualConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'metric_visual'
    name = 'django_spire.metric.visual'

    MODEL_PERMISSIONS = (
        {
            'name': 'metric_visual',
            'model_class_path': 'django_spire.metric.visual.models.Visual',
            'is_proxy_model': False
        },
    )
