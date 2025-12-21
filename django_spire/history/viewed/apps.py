from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class HistoryViewedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_history_viewed'
    name = 'django_spire.history.viewed'

    REQUIRED_APPS = ('django_spire_core', 'django_spire_history')

    def ready(self) -> None:
        check_required_apps(self.label)
