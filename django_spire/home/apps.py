from __future__ import annotations

from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'spire_home'
    name = 'django_spire.home'
