from dandy.workflow import BaseWorkflow
from dandy.llm import LlmBot
from django.core.handlers.wsgi import WSGIRequest


class ChatWorkflow(BaseWorkflow):
    @classmethod
    def process(
            cls,
            request: WSGIRequest,
            user_input: str,
    ):
        response = LlmBot.process(user_input)

        return {
            'text': response.text
        }
