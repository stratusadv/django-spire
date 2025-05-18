import json

from django.conf import settings
from django.http import HttpResponse

from django_spire.ai.chat.messages import DefaultMessageIntel
from django_spire.ai.chat.models import Chat
from django_spire.ai.chat.responses import MessageResponse
from django_spire.ai.chat.choices import MessageResponseType
from django_spire.ai.chat.tools import chat_workflow_process
from django_spire.consts import AI_CHAT_WORKFLOW_SETTINGS_NAME


def response_message_render_view(request):
    body_data = json.loads(request.body)

    chat_workflow_name = getattr(settings, AI_CHAT_WORKFLOW_SETTINGS_NAME)

    if chat_workflow_name is None:
        raise ValueError(
            f'"{AI_CHAT_WORKFLOW_SETTINGS_NAME}" must be set in the django settings.'
        )

    chat = Chat.objects.by_user(request.user).get(id=body_data['chat_id'])

    message_intel = chat_workflow_process(
        request,
        body_data['message_body'],
        message_history=chat.generate_message_history(),
    )

    llm_message = MessageResponse(
        type=MessageResponseType.RESPONSE,
        sender=chat_workflow_name,
        message_intel=message_intel,
    )

    chat.add_message_response(llm_message)

    return HttpResponse(llm_message.render_to_html_string({'chat_id': chat.id}))
