from __future__ import annotations

from django.apps import AppConfig

from django_spire.tools import check_required_apps


class SignageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_metric_visual_signage'
    name = 'django_spire.metric.visual.signage'
    verbose_name = 'DJANGO_SPIRE_METRIC_VISUAL_SIGNAGE'

    MODEL_PERMISSIONS = (
        {
            'name': 'visual_signage',
            'verbose_name': 'Visual Signage',
            'model_class_path': 'django_spire.metric.visual.signage.models.Signage',
            'is_proxy_model': False,
        },
        {
            'name': 'visual_signage_presentation',
            'verbose_name': 'Visual Signage Presentation',
            'model_class_path': 'django_spire.metric.visual.signage.models.SignagePresentation',
            'is_proxy_model': False,
        },
    )

    REQUIRED_APPS = (
        'django_spire_core',
        'django_spire_metric_domain',
        'django_spire_metric_visual',
        'django_spire_metric_visual_presentation',
    )

    def ready(self) -> None:
        check_required_apps(self.label)
