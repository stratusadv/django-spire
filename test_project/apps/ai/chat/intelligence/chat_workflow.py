from dandy.recorder import recorder_to_html_file
from dandy.workflow import BaseWorkflow
from dandy.llm import LlmBot, MessageHistory
from django.core.handlers.wsgi import WSGIRequest

from django_spire.ai.chat.message_intel import DefaultMessageIntel, BaseMessageIntel
from django_spire.knowledge.intelligence.workflows.knowledge_workflow import KnowledgeWorkflow
from test_project.apps.ai.chat.intelligence.intent_map import IntentLlmMap
from test_project.apps.ai.chat.intelligence.prompts import test_project_company_prompt
from test_project.apps.ai.chat.messages import ClownFlyingDistanceMessageIntel, PirateMessageIntel


class ChatWorkflow(BaseWorkflow):
    @classmethod
    @recorder_to_html_file('chat_workflow')
    def process(
            cls,
            request: WSGIRequest,
            user_input: str,
            message_history: MessageHistory | None = None
    ) -> BaseMessageIntel:

        intents = IntentLlmMap.process(
            user_input,
            max_return_values=1
        )


        if intents[0] == 'clowns':
            response = LlmBot.process(
                prompt=user_input,
                intel_class=ClownFlyingDistanceMessageIntel,
                message_history=message_history,
            )

        elif intents[0] == 'pirates':
            response = LlmBot.process(
                prompt=user_input,
                intel_class=PirateMessageIntel,
                message_history=message_history,
            )

        elif intents[0] == 'knowledge':
            return KnowledgeWorkflow.process(
                user_input=user_input
            )

        else:
            response = LlmBot.process(
                prompt=user_input,
                intel_class=DefaultMessageIntel,
                message_history=message_history,
                postfix_system_prompt=test_project_company_prompt()
            )


        return response
