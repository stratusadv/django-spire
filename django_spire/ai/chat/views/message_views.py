from django.http import HttpResponse

from django_spire.ai.chat.models import Chat
from django_spire.ai.chat.responses import MessageResponseGroup


def load_messages_render_view(request, chat_id):
    chat = (
        Chat.objects
        .by_user(request.user)
        .get(id=chat_id)
    )

    message_group = MessageResponseGroup()

    for chat_message in chat.messages.all():
        message_group.add_message_response(
            chat_message.to_message_response()
        )

    return HttpResponse(
        message_group.render_to_html_string(
            {
                'chat_id': chat.id,
            }
        )
    )
