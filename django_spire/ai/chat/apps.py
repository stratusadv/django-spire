from django.apps import AppConfig

from django_spire.tools import check_required_apps


class AiChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.ai.chat'
    label = 'spire_ai_chat'

    REQUIRED_APPS = ('spire_ai',)

    def ready(self) -> None:
        check_required_apps(self.label)
