from __future__ import annotations

from django.apps import AppConfig


class DjangoSpireConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_core'
    name = 'django_spire.core'
    verbose_name = 'Core (Django Spire)'

    URLPATTERNS_INCLUDE = 'django_spire.core.urls'
    URLPATTERNS_NAMESPACE = 'core'

    def ready(self) -> None:
        from django_spire.contrib.admin.site import apply_admin_site_title  # noqa: PLC0415
        import django_spire.core.signals  # noqa: F401, PLC0415

        apply_admin_site_title()
