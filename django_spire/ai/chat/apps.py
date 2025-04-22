from django.apps import AppConfig
from django.conf import settings

from django_spire.consts import AI_CHAT_WORKFLOW_CLASS_SETTINGS_NAME
from django_spire.utils import check_required_apps


class AiChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.ai.chat'
    label = 'django_spire_ai_chat'

    REQUIRED_APPS = ('django_spire_ai',)

    def ready(self) -> None:
        if not isinstance(getattr(settings, AI_CHAT_WORKFLOW_CLASS_SETTINGS_NAME), str):
            raise ValueError(f'"{AI_CHAT_WORKFLOW_CLASS_SETTINGS_NAME}" must be set in the django settings when using "{self.label}".')

        check_required_apps(self.label)
