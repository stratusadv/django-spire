from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class ReportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'report'
    name = 'django_spire.metric.report'

    MODEL_PERMISSIONS = (
        {
            'name': 'report',
            'verbose_name': 'Report',
            'model_class_path': 'django_spire.metric.report.models.ReportRun',
            'is_proxy_model': False,
        },
    )

    REQUIRED_APPS = ('django_spire_core',)

    def ready(self) -> None:
        check_required_apps(self.label)
