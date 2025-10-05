from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.ai.sms.intel import SmsIntel
from test_project.apps.ai.chat.intelligence.workflows.chat_workflow import ChatWorkflow

if TYPE_CHECKING:
    from dandy.llm.request.message import MessageHistory
    from django.core.handlers.wsgi import WSGIRequest


class SmsConversationWorkflow:
    @staticmethod
    def process(
        request: WSGIRequest,
        user_input: str,
        message_history: MessageHistory | None = None
    ) -> SmsIntel:
        return SmsIntel(
            body=str(
                ChatWorkflow.process(
                    request,
                    user_input=user_input,
                    message_history=message_history,
                )
            )
        )
