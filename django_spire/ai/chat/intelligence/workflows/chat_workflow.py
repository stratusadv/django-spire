from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from dandy.recorder import recorder_to_html_file

from django_spire.ai.chat.intelligence.decoders.tools import generate_intent_decoder
from django_spire.ai.decorators import log_ai_interaction_from_recorder
from django_spire.conf import settings
from django_spire.core.utils import (
    get_callable_from_module_string_and_validate_arguments,
)
from django_spire.ai.chat.message_intel import BaseMessageIntel

if TYPE_CHECKING:
    from dandy.llm.request.message import MessageHistory
    from django.core.handlers.wsgi import WSGIRequest


@recorder_to_html_file('spire_ai_chat_workflow')
def chat_workflow(
    request: WSGIRequest, user_input: str, message_history: MessageHistory | None = None
) -> BaseMessageIntel:

    if settings.AI_CHAT_DEFAULT_CALLABLE is not None:
        default_process = get_callable_from_module_string_and_validate_arguments(
                module_string=settings.AI_CHAT_DEFAULT_CALLABLE,
                valid_args=('request', 'user_input', 'message_history'),
            )
    else:
        default_process = None

    intent_decoder = generate_intent_decoder(
        request=request,
        default_callable=default_process,
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

    if message_intel is None and default_process is not None:
        message_intel = run_workflow_process(default_process)

    if not issubclass(message_intel.__class__, BaseMessageIntel):
        message = f'{intent_process.__qualname__} must return an instance of a {BaseMessageIntel.__name__} sub class.'
        raise TypeError(message)

    return message_intel

