from dandy.workflow import BaseWorkflow
from dandy.llm import LlmBot, MessageHistory
from django.core.handlers.wsgi import WSGIRequest


class ChatWorkflow(BaseWorkflow):
    @classmethod
    def process(
            cls,
            request: WSGIRequest,
            user_input: str,
            message_history: MessageHistory | None = None
    ):
        response = LlmBot.process(
            prompt=user_input,
            message_history=message_history,
        )

        return {
            'text': response.text
        }
