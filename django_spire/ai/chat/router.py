from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from dandy import recorder_to_html_file

from django_spire.ai.chat.intelligence.decoders.intent_decoder import generate_intent_decoder
from django_spire.ai.chat.message_intel import BaseMessageIntel, DefaultMessageIntel
from django_spire.ai.decorators import log_ai_interaction_from_recorder

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
        from django_spire.knowledge.intelligence.workflows.knowledge_workflow import (
            knowledge_search_workflow,
        )

        if request.user.has_perm('django_spire_knowledge.view_collection'):
            return knowledge_search_workflow(
                request=request,
                user_input=user_input,
                message_history=message_history
            )

        return DefaultMessageIntel(
            text='Sorry, I could not find any information on that.'
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

        intent_process = intent_decoder().process(user_input, max_return_values=1)[0]

        return intent_process(
            request=request,
            user_input=user_input,
            message_history=message_history
        )
