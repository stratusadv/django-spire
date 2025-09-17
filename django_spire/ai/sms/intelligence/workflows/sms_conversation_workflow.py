from dandy.recorder import recorder_to_html_file
from dandy.workflow import BaseWorkflow
from dandy.llm import MessageHistory
from django.core.handlers.wsgi import WSGIRequest

from django_spire.ai.chat.intelligence.workflows.chat_workflow import SpireChatWorkflow
from django_spire.ai.sms.intel import SmsIntel


class SpireSmsConversationWorkflow(BaseWorkflow):
    @classmethod
    @recorder_to_html_file('sms_workflow')
    def process(
            cls,
            request: WSGIRequest,
            user_input: str,
            message_history: MessageHistory | None = None
    ) -> SmsIntel:
        return SmsIntel(
            body=str(
                SpireChatWorkflow.process(
                    request,
                    user_input=user_input,
                    message_history=message_history,
                )
            )
        )
