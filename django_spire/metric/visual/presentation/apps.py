from __future__ import annotations

from django.apps import AppConfig


class PresentationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'visual_presentation'
    name = 'django_spire.metric.visual.presentation'

    MODEL_PERMISSIONS = (
        {
            'name': 'visual_presentation',
            'model_class_path': 'django_spire.metric.visual.presentation.models.Presentation',
            'is_proxy_model': False
        },
    )
