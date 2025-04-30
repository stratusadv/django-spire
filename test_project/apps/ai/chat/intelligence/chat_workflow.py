from dandy.workflow import BaseWorkflow
from dandy.llm import LlmBot, MessageHistory
from django.core.handlers.wsgi import WSGIRequest

from test_project.apps.ai.chat.intelligence.prompts import test_project_company_prompt


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
            postfix_system_prompt=test_project_company_prompt()
        )

        return {
            'text': response.text
        }
