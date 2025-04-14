from dandy.workflow import BaseWorkflow
from dandy.llm import LlmBot, MessageHistory
from django.core.handlers.wsgi import WSGIRequest

from example.ai.chat.intelligence.prompts import example_company_prompt


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
            postfix_system_prompt=example_company_prompt()
        )

        return {
            'text': response.text
        }
