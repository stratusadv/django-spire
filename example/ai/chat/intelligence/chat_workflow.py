from dandy.workflow import BaseWorkflow
from django.core.handlers.wsgi import WSGIRequest


class ChatWorkflow(BaseWorkflow):
    @classmethod
    def process(
            cls,
            request: WSGIRequest,
            user_input: str,
    ):
        return {
            'text': 'Hello from the chat workflow'
        }
