from dandy.workflow import BaseWorkflow
from dandy.llm import MessageHistory
from django.core.handlers.wsgi import WSGIRequest

from django_spire.ai.sms.intel import SmsIntel
from test_project.apps.ai.chat.intelligence.workflows.chat_workflow import ChatWorkflow


class SmsConversationWorkflow(BaseWorkflow):
    @classmethod
    def process(
            cls,
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
