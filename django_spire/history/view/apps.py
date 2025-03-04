from django.apps import AppConfig


class HistoryViewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'spire_history_view'
    name = 'django_spire.history.view'
