from __future__ import annotations

from django.apps import AppConfig


class HistoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'spire_history'
    name = 'django_spire.history'
