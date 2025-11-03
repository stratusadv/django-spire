from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponse

from django_spire.ai.chat.models import Chat
from django_spire.ai.chat.responses import MessageResponseGroup

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def load_messages_render_view(request: WSGIRequest, chat_id: int) -> HttpResponse:
    chat = (
        Chat.objects
        .by_user(request.user)
        .get(id=chat_id)
    )

    message_group = MessageResponseGroup()

    for chat_message in chat.messages.newest_by_count_reversed(20):
        message_group.add_message_response(
            chat_message.to_message_response()
        )

    return HttpResponse(
        message_group.render_to_html_string(
            {
                'chat_id': chat.id,
                'is_loading': True,
            }
        )
    )
