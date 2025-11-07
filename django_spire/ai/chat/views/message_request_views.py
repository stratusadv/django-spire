from __future__ import annotations

import json

from typing import TYPE_CHECKING

from django.conf import settings
from django.http import HttpResponse
from django.utils.timezone import now

from django_spire.ai.chat.choices import MessageResponseType
from django_spire.ai.chat.message_intel import DefaultMessageIntel
from django_spire.ai.chat.models import Chat
from django_spire.ai.chat.responses import MessageResponse, MessageResponseGroup

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def request_message_render_view(request: WSGIRequest) -> HttpResponse:
    body_data = json.loads(request.body)

    chat_id = body_data['chat_id']

    current_datetime = now()
    formatted_timestamp = current_datetime.strftime('%b %d, %Y at %I:%M %p')

    if chat_id in {0, '0', ''}:
        chat = Chat.objects.create(
            user=request.user,
            name=body_data['message_body'],
            last_message_datetime=current_datetime
        )
    else:
        chat = (
            Chat.objects
            .by_user(request.user)
            .get(id=chat_id)
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
        ),
        message_timestamp=formatted_timestamp
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
            ),
            synthesis_speech=body_data.get('synthesis_speech', False),
        )
    )

    return HttpResponse(
        message_response_group.render_to_html_string(
            context_data={
                "chat_id": chat.id,
                "chat_workflow_name": settings.AI_PERSONA_NAME,
            }
        )
    )
