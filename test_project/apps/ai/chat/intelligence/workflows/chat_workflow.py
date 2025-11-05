from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.recorder import recorder_to_html_file
from dandy import Bot, Prompt

from django_spire.ai.chat.message_intel import BaseMessageIntel, DefaultMessageIntel
from django_spire.ai.chat.intelligence.prompts import organization_prompt
from test_project.apps.ai.chat.intelligence.maps.intent_map import IntentDecoder
from test_project.apps.ai.chat.intelligence.message_intels import (
    ClownFlyingDistanceMessageIntel,
    PirateMessageIntel
)

if TYPE_CHECKING:
    from dandy.llm.request.message import MessageHistory
    from django.core.handlers.wsgi import WSGIRequest


class ChatWorkflow:
    @staticmethod
    @recorder_to_html_file('chat_workflow')
    def process(
        request: WSGIRequest,
        user_input: str,
        message_history: MessageHistory | None = None
    ) -> BaseMessageIntel:
        decoder = IntentDecoder()

        decoder.mapping = {
            'The user wants to talk about a clown or clowns.': 'clowns',
            'The user wants to talk about a pirate or pirates.': 'pirates',
            'The user does not want to talk about clowns or pirates': 'default',
        }

        intents = decoder.process(
            user_input,
            max_return_values=1
        )

        bot = Bot()

        if intents[0] == 'clowns':
            response = bot.llm.prompt_to_intel(
                prompt=user_input,
                intel_class=ClownFlyingDistanceMessageIntel,
                message_history=message_history,
            )

        elif intents[0] == 'pirates':
            response = bot.llm.prompt_to_intel(
                prompt=user_input,
                intel_class=PirateMessageIntel,
                message_history=message_history,
            )

        else:
            response = bot.llm.prompt_to_intel(
                prompt=(
                    Prompt()
                    .text(user_input)
                    .line_break()
                    .prompt(organization_prompt())
                ),
                intel_class=DefaultMessageIntel,
                message_history=message_history
            )

        return response
