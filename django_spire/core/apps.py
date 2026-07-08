from __future__ import annotations

from django.apps import AppConfig


class DjangoSpireConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_core'
    name = 'django_spire.core'

    def ready(self) -> None:
        import django_spire.core.signals  # noqa: F401, PLC0415
