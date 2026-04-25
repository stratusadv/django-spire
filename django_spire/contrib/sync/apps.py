from __future__ import annotations

from django.apps import AppConfig


class SyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'sync'
    name = 'django_spire.contrib.sync'
