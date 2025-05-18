import json

from django.conf import settings
from django.http import HttpResponse

from django_spire.ai.chat.messages import DefaultMessageIntel
from django_spire.ai.chat.models import Chat
from django_spire.ai.chat.responses import MessageResponseGroup, MessageResponse
from django_spire.ai.chat.choices import MessageResponseType
from django_spire.consts import AI_CHAT_WORKFLOW_SETTINGS_NAME


def request_message_render_view(request):
    body_data = json.loads(request.body)

    chat = (
        Chat.objects
        .by_user(request.user)
        .get(id=body_data['chat_id'])
    )

    if chat.is_empty:
        chat.name = body_data['message_body']
        chat.save()

    message_response_group = MessageResponseGroup()

    user_message_response = MessageResponse(
        type=MessageResponseType.REQUEST,
        sender='You',
        message_intel=DefaultMessageIntel(
            text=body_data['message_body']
        )
    )

    message_response_group.add_message_response(
        user_message_response
    )

    chat.add_message_response(user_message_response)

    message_response_group.add_message_response(
        MessageResponse(
            type=MessageResponseType.LOADING_RESPONSE,
            sender='Spire',
            message_intel=DefaultMessageIntel(
                text=body_data['message_body']
            )
        )
    )

    return HttpResponse(
        message_response_group.render_to_html_string(
            context_data={
                "chat_id": chat.id,
                "chat_workflow_name": getattr(settings, AI_CHAT_WORKFLOW_SETTINGS_NAME),
            }
        )
    )
