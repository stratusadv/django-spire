from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Prompt
from dandy.recorder import recorder_to_html_file

from django_spire.ai.chat.intelligence.bots.chat_bot import ChatBot
from django_spire.ai.chat.intelligence.maps.intent_llm_map import IntentDecoder
from django_spire.ai.chat.message_intel import DefaultMessageIntel
from django_spire.auth.controller.controller import AppAuthController

if TYPE_CHECKING:
    from dandy.llm.request.message import MessageHistory
    from django.core.handlers.wsgi import WSGIRequest

    from django_spire.ai.chat.message_intel import BaseMessageIntel


class SpireChatWorkflow:
    @staticmethod
    def _generate_intent_decoder(request: WSGIRequest) -> IntentDecoder:
        from django_spire.knowledge.intelligence.workflows.knowledge_workflow import KnowledgeWorkflow

        intent_dict = {}

        if AppAuthController(app_name='knowledge', request=request).can_view():
            intent_message = (
                'The user is looking for information or knowledge on something.'
            )

            intent_dict[intent_message] = KnowledgeWorkflow

        intent_dict['None of the above choices match the user\'s intent'] = None

        decoder = IntentDecoder()
        decoder.mapping = intent_dict
        return decoder

    @staticmethod
    @recorder_to_html_file('spire_chat_workflow')
    def process(
        request: WSGIRequest,
        user_input: str,
        message_history: MessageHistory | None = None
    ) -> BaseMessageIntel:
        intent_decoder = SpireChatWorkflow._generate_intent_decoder(request)
        intents = intent_decoder.process(user_input, max_return_values=1)

        chat_bot = ChatBot()

        if intents[0] is None:
            return chat_bot.llm.prompt_to_intel(
                prompt=user_input,
                intel_class=DefaultMessageIntel,
                message_history=message_history
            )

        return chat_bot.llm.prompt_to_intel(
            prompt=(
                Prompt()
                .text(f'User Input: {user_input}')
                .line_break()
                .text(intents[0].process(user_input))
            ),
            intel_class=DefaultMessageIntel,
            message_history=message_history
        )
