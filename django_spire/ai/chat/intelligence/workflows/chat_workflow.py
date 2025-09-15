from __future__ import annotations

from typing import TYPE_CHECKING, Type

from dandy.map import Map
from dandy.recorder import recorder_to_html_file
from dandy.workflow import BaseWorkflow
from dandy.llm import LlmBot, MessageHistory, Prompt
from django.core.handlers.wsgi import WSGIRequest

from django_spire.ai.chat.intelligence.maps.intent_llm_map import IntentLlmMap
from django_spire.ai.chat.intelligence.prompts import organization_prompt
from django_spire.ai.chat.message_intel import DefaultMessageIntel
from django_spire.auth.controller.controller import AppAuthController
from django_spire.knowledge.intelligence.workflows.knowledge_workflow import \
    KnowledgeWorkflow


if TYPE_CHECKING:
    from django_spire.ai.chat.message_intel import BaseMessageIntel


class SpireChatWorkflow(BaseWorkflow):
    @classmethod
    def _generate_intent_map(cls, request: WSGIRequest) -> Type[IntentLlmMap]:
        intent_dict = {}

        if AppAuthController(app_name='knowledge', request=request).can_view():
            intent_message = (
                'The user is looking for information or knowledge on something.'
            )
            intent_dict[intent_message] = KnowledgeWorkflow

        intent_dict['None of the above choices match the user\'s intent'] = None

        IntentLlmMap.map = Map(intent_dict)
        IntentLlmMap._map_enum = IntentLlmMap.map.as_enum()
        return IntentLlmMap

    @classmethod
    @recorder_to_html_file('spire_chat_workflow')
    def process(
            cls,
            request: WSGIRequest,
            user_input: str,
            message_history: MessageHistory | None = None
    ) -> BaseMessageIntel:
        intent_map = cls._generate_intent_map(request)
        intents = intent_map.process(user_input, max_return_values=1)

        if intents[0] is None:
            response = LlmBot.process(
                prompt=user_input,
                message_history=message_history,
                postfix_system_prompt=organization_prompt()
            )

            return DefaultMessageIntel(text=response.text)

        response = LlmBot.process(
            prompt=(
                Prompt()
                .text(f'User Input: {user_input}')
                .line_break()
                .text(
                    'Use the following information to the answer the user\'s question '
                    'or concern.'
                )
                .line_break()
                .text(intents[0].process(user_input))
            ),
            message_history=message_history,
            postfix_system_prompt=organization_prompt()
        )

        return DefaultMessageIntel(text=response.text)
