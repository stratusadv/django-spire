import json

from django.template.response import TemplateResponse
from django.utils.timezone import now

from django_spire.ai.chat.models import Chat
from django_spire.core.shortcuts import get_object_or_null_obj


def confirm_delete_view(request, pk: int) -> TemplateResponse:
    return TemplateResponse(
        request,
        context={'chat': get_object_or_null_obj(Chat, pk=pk)},
        template='django_spire/ai/chat/section/confirm_delete_section.html'
    )


def load_chat_view(request) -> TemplateResponse:
    body_data = json.loads(request.body)

    chat_id = body_data['chat_id']

    if chat_id == 0:
        chat = Chat.objects.get_empty_or_create(
            user=request.user
        )
        chat.name = 'New Chat'
        chat.last_message_datetime = now()
        chat.save()

    else:
        chat = Chat.objects.get(
            id=chat_id,
            user=request.user,
        )

    return TemplateResponse(
        request,
        context={
            'chat': chat,
            'top_nav_height_px': body_data['top_nav_height_px']
        },
        template='django_spire/ai/chat/widget/dialog_widget.html'
    )


def recent_chat_list_view(request) -> TemplateResponse:
    return TemplateResponse(
        request,
        context={
            'recent_chats': (
                Chat.objects
                .by_user(request.user)
                .order_by('-last_message_datetime')
                .active()
            )[:20]
        },
        template='django_spire/ai/chat/widget/recent_chat_list_widget.html'
    )


def search_chat_view(request) -> TemplateResponse:
    body_data = json.loads(request.body)
    chats = Chat.objects.by_user(request.user).search(body_data['query'])

    return TemplateResponse(
        request,
        context={
            'search_results': [
                {
                    'name': chat.name,
                    'id': chat.id,
                } for chat in chats
            ]
        },
        template='django_spire/ai/chat/widget/search_chat_results_widget.html'
    )
