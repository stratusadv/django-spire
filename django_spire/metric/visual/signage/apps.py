from __future__ import annotations

from django.apps import AppConfig


class SignageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'visual_signage'
    name = 'django_spire.metric.visual.signage'

    MODEL_PERMISSIONS = (
        {
            'name': 'visual_signage',
            'model_class_path': 'django_spire.metric.visual.signage.models.Signage',
            'is_proxy_model': False
        },
    )
