from dandy.workflow import BaseWorkflow
from dandy.llm import LlmBot, MessageHistory
from django.core.handlers.wsgi import WSGIRequest

from django_spire.ai.chat.messages import DefaultMessageIntel, BaseMessageIntel
from test_project.apps.ai.chat.intelligence.prompts import test_project_company_prompt
from test_project.apps.ai.chat.messages import ClownFlyingDistanceMessageIntel


class ChatWorkflow(BaseWorkflow):
    @classmethod
    def process(
            cls,
            request: WSGIRequest,
            user_input: str,
            message_history: MessageHistory | None = None
    ) -> BaseMessageIntel:

        # response = LlmBot.process(
        #     prompt=user_input,
        #     intel_class=DefaultMessageIntel,
        #     message_history=message_history,
        #     postfix_system_prompt=test_project_company_prompt()
        # )

        response = LlmBot.process(
            prompt=user_input,
            intel_class=ClownFlyingDistanceMessageIntel,
            message_history=message_history,
            postfix_system_prompt=test_project_company_prompt()
        )

        return response
