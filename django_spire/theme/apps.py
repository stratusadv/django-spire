from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class ThemeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_theme'
    name = 'django_spire.theme'

    REQUIRED_APPS = ('django_spire_core',)

    def ready(self) -> None:
        check_required_apps(self.label)
