from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from dandy import Bot
from dandy.recorder import recorder_to_html_file

from django_spire.ai.chat.intelligence.decoders.tools import generate_intent_decoder
from django_spire.ai.chat.message_intel import BaseMessageIntel, DefaultMessageIntel
from django_spire.ai.decorators import log_ai_interaction_from_recorder

if TYPE_CHECKING:
    from dandy.llm.request.message import MessageHistory
    from django.core.handlers.wsgi import WSGIRequest


def SpireChatWorkflow(
    request: WSGIRequest,
    user_input: str,
    message_history: MessageHistory | None = None
) -> BaseMessageIntel:
    return chat_workflow(
        request=request,
        user_input=user_input,
        message_history=message_history
    )


def default_chat_response(
    request: WSGIRequest,
    user_input: str,
    message_history: MessageHistory | None = None
) -> BaseMessageIntel:
    bot = Bot()
    return bot.llm.prompt_to_intel(
        prompt=user_input,
        intel_class=DefaultMessageIntel,
        message_history=message_history,
    )


@recorder_to_html_file('spire_ai_chat_workflow')
def chat_workflow(
    request: WSGIRequest,
    user_input: str,
    message_history: MessageHistory | None = None
) -> BaseMessageIntel:
    intent_decoder = generate_intent_decoder(
        request=request,
        default_callable=default_chat_response,
    )

    intent_process = intent_decoder.process(user_input, max_return_values=1)[0]

    @log_ai_interaction_from_recorder(request.user)
    def run_workflow_process(callable_: Callable) -> BaseMessageIntel | None:
        return callable_(
            request=request,
            user_input=user_input,
            message_history=message_history,
        )

    message_intel = run_workflow_process(intent_process)

    if not isinstance(message_intel, BaseMessageIntel):
        if message_intel is None:
            return default_chat_response(
                request=request,
                user_input=user_input,
                message_history=message_history
            )

        message = f'{intent_process.__qualname__} must return an instance of a {BaseMessageIntel.__name__} sub class.'
        raise TypeError(message)

    return message_intel
