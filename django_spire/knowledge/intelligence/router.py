from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot, Prompt

from django_spire.ai.chat.message_intel import BaseMessageIntel, DefaultMessageIntel
from django_spire.ai.chat.router import BaseChatRouter
from django_spire.conf import settings
from django_spire.knowledge.intelligence.workflows.knowledge_workflow import (
    NO_KNOWLEDGE_MESSAGE_INTEL,
    knowledge_search_workflow,
)

if TYPE_CHECKING:
    from dandy.llm.request.message import MessageHistory
    from django.core.handlers.wsgi import WSGIRequest


class KnowledgeSearchRouter(BaseChatRouter):
    def _default_chat_callable(
        self,
        request: WSGIRequest,
        user_input: str,
        message_history: MessageHistory | None = None
    ) -> BaseMessageIntel:
        persona_name = getattr(settings, 'DJANGO_SPIRE_AI_PERSONA_NAME', 'AI Assistant')

        system_prompt = (
            Prompt()
            .text(f'You are {persona_name}, a helpful AI assistant.')
            .line_break()
            .text('Important rules:')
            .list([
                f'You should always identify yourself as {persona_name}.',
                'Please never mention being Qwen, Claude, GPT, or any other model name.',
                'Be helpful, friendly, and professional.',
            ])
        )

        bot = Bot()
        bot.role = system_prompt

        return bot.llm.prompt_to_intel(
            prompt=user_input,
            intel_class=DefaultMessageIntel,
            message_history=message_history,
        )

    def workflow(
        self,
        request: WSGIRequest,
        user_input: str,
        message_history: MessageHistory | None = None
    ) -> BaseMessageIntel:
        knowledge_result = knowledge_search_workflow(
            request=request,
            user_input=user_input,
            message_history=message_history
        )

        if knowledge_result == NO_KNOWLEDGE_MESSAGE_INTEL:
            return self._default_chat_callable(
                request=request,
                user_input=user_input,
                message_history=message_history
            )

        return knowledge_result
