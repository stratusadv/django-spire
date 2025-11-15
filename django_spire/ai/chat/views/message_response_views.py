from __future__ import annotations

import json

from typing import TYPE_CHECKING

from django.conf import settings
from django.http import HttpResponse
from django.utils.timezone import now

from django_spire.ai.chat.choices import MessageResponseType
from django_spire.ai.chat.intelligence.workflows.chat_workflow import chat_workflow
from django_spire.ai.chat.models import Chat
from django_spire.ai.chat.responses import MessageResponse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def response_message_render_view(request: WSGIRequest) -> HttpResponse:
    body_data = json.loads(request.body)

    chat = Chat.objects.by_user(request.user).get(id=body_data['chat_id'])

    message_intel = chat_workflow(
        request,
        body_data['message_body'],
        message_history=chat.generate_message_history(),
    )

    current_datetime = now()
    formatted_timestamp = current_datetime.strftime('%b %d, %Y at %I:%M %p')

    response_message = MessageResponse(
        type=MessageResponseType.RESPONSE,
        sender=getattr(settings, 'DJANGO_SPIRE_AI_PERSONA_NAME', 'AI Assistant'),
        message_intel=message_intel,
        synthesis_speech=body_data.get('synthesis_speech', False),
        message_timestamp=formatted_timestamp
    )

    chat.add_message_response(response_message)

    return HttpResponse(response_message.render_to_html_string({'chat_id': chat.id}))
