from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class AiChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_spire.ai.chat'
    label = 'django_spire_ai_chat'
    MODEL_PERMISSIONS = (
        {
            'name': 'ai_chat',
            'verbose_name': 'AI Chat',
            'model_class_path': 'django_spire.ai.chat.models.Chat',
            'is_proxy_model': False,
        },
    )

    REQUIRED_APPS = ('django_spire_ai', 'django_spire_ai_context')

    def ready(self) -> None:
        check_required_apps(self.label)
