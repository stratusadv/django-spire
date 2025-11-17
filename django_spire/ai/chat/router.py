from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from dandy import Bot, Prompt
from dandy.recorder import recorder_to_html_file

from django_spire.ai.chat.intelligence.decoders.intent_decoder import generate_intent_decoder
from django_spire.ai.chat.message_intel import BaseMessageIntel, DefaultMessageIntel
from django_spire.ai.decorators import log_ai_interaction_from_recorder
from django_spire.conf import settings

if TYPE_CHECKING:
    from dandy.llm.request.message import MessageHistory
    from django.core.handlers.wsgi import WSGIRequest


class BaseChatRouter(ABC):
    @abstractmethod
    def workflow(
        self,
        request: WSGIRequest,
        user_input: str,
        message_history: MessageHistory | None = None
    ) -> BaseMessageIntel:
        raise NotImplementedError

    @recorder_to_html_file('spire_ai_chat_workflow')
    def process(
        self,
        request: WSGIRequest,
        user_input: str,
        message_history: MessageHistory | None = None
    ) -> BaseMessageIntel:
        @log_ai_interaction_from_recorder(request.user)
        def run_workflow_process() -> BaseMessageIntel | None:
            return self.workflow(
                request=request,
                user_input=user_input,
                message_history=message_history,
            )

        message_intel = run_workflow_process()

        if not isinstance(message_intel, BaseMessageIntel):
            if message_intel is None:
                return DefaultMessageIntel(
                    text='I apologize, but I was unable to process your request.'
                )

            message = f'{self.__class__.__name__}.workflow must return an instance of a {BaseMessageIntel.__name__} sub class.'
            raise TypeError(message)

        return message_intel


class SpireChatRouter(BaseChatRouter):
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
        bot.llm_role = system_prompt

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
        intent_decoder = generate_intent_decoder(
            request=request,
            default_callable=self._default_chat_callable,
        )

        intent_process = intent_decoder.process(user_input, max_return_values=1)[0]

        return intent_process(
            request=request,
            user_input=user_input,
            message_history=message_history
        )
