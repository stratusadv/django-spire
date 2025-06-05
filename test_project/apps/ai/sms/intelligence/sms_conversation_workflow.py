from dandy.recorder import recorder_to_html_file
from dandy.workflow import BaseWorkflow
from dandy.llm import LlmBot, MessageHistory
from django.core.handlers.wsgi import WSGIRequest

from django_spire.ai.sms.intel import SmsIntel
from test_project.apps.ai.sms.intelligence.llm_maps import IntentLlmMap
from test_project.apps.ai.sms.intelligence.prompts import test_project_company_prompt


class SmsConversationWorkflow(BaseWorkflow):
    @classmethod
    # @recorder_to_html_file('sms_conversation_workflow')
    def process(
            cls,
            request: WSGIRequest,
            user_input: str,
            message_history: MessageHistory | None = None
    ) -> SmsIntel:

        intents = IntentLlmMap.process(user_input, max_return_values=1)

        if intents[0] == 'clowns':
            response = LlmBot.process(
                prompt=user_input,
                intel_class=SmsIntel,
                message_history=message_history,
            )

        elif intents[0] == 'pirates':
            response = LlmBot.process(
                prompt=user_input,
                intel_class=SmsIntel,
                message_history=message_history,
            )

        else:
            response = LlmBot.process(
                prompt=user_input,
                intel_class=SmsIntel,
                message_history=message_history,
                postfix_system_prompt=test_project_company_prompt()
            )


        return response
