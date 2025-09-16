from dandy.recorder import recorder_to_html_file
from dandy.workflow import BaseWorkflow
from dandy.llm import LlmBot, MessageHistory
from django.core.handlers.wsgi import WSGIRequest

from django_spire.ai.chat.message_intel import BaseMessageIntel
from test_project.apps.ai.chat.intelligence.maps.intent_map import IntentLlmMap
from test_project.apps.ai.chat.intelligence.message_intels import \
    ClownFlyingDistanceMessageIntel, PirateMessageIntel


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

        else:
            response = intents[0].process(
                request=request,
                user_input=user_input,
                message_history=message_history
            )

        return response
