from django.apps import AppConfig


class HistoryViewedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'spire_history_viewed'
    name = 'django_spire.history.viewed'
