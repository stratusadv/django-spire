from __future__ import annotations

from django.apps import AppConfig


class BreadcrumbsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_breadcrumb'
    name = 'django_spire.contrib.breadcrumb'
