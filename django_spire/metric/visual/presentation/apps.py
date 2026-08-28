from __future__ import annotations

from django.apps import AppConfig

from django_spire.tools import check_required_apps


class PresentationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_metric_visual_presentation'
    name = 'django_spire.metric.visual.presentation'
    verbose_name = 'DJANGO_SPIRE_METRIC_VISUAL_PRESENTATION'

    MODEL_PERMISSIONS = (
        {
            'name': 'visual_presentation',
            'verbose_name': 'Visual Presentation',
            'model_class_path': 'django_spire.metric.visual.presentation.models.Presentation',
            'is_proxy_model': False,
        },
        {
            'name': 'visual_presentation_slide',
            'verbose_name': 'Visual Presentation Slide',
            'model_class_path': 'django_spire.metric.visual.presentation.models.Slide',
            'is_proxy_model': False,
        },
        {
            'name': 'visual_presentation_slide_section',
            'verbose_name': 'Visual Presentation Slide Section',
            'model_class_path': 'django_spire.metric.visual.presentation.models.SlideSection',
            'is_proxy_model': False,
        },
    )

    REQUIRED_APPS = (
        'django_spire_core',
        'django_spire_metric_domain',
        'django_spire_metric_visual',
    )

    def ready(self) -> None:
        check_required_apps(self.label)
