from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.recorder import recorder_to_html_file

from django_spire.ai.chat.intelligence.workflows.chat_workflow import chat_workflow
from django_spire.ai.sms.intel import SmsIntel

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from dandy.llm.request.message import MessageHistory


@recorder_to_html_file('spire_ai_sms_conversation_workflow')
def sms_conversation_workflow(
    request: WSGIRequest, user_input: str, message_history: MessageHistory | None = None
) -> SmsIntel:
    return SmsIntel(
        body=str(
            chat_workflow(
                request,
                user_input=user_input,
                message_history=message_history,
            )
        )
    )
