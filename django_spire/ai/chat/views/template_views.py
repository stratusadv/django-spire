import json

from django.template.response import TemplateResponse
from django.utils.timezone import now

from django_spire.ai.chat.models import Chat


def load_template_view(request):
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
        'django_spire/ai/chat/widget/dialog_widget.html',
        {
            'chat': chat,
            'top_nav_height_px': body_data['top_nav_height_px']
        }
    )

def recent_template_view(request):
    chats = (
        Chat.objects
        .by_user(request.user)
        .order_by('-last_message_datetime')
    )[:20]

    return TemplateResponse(
        request,
        'django_spire/ai/chat/widget/recent_chat_list_widget.html',
        {
            'recent_chats': [
                {
                    'name': chat.name_shortened,
                    'id': chat.id,
                } for chat in chats
            ]
        }
    )

def search_template_view(request):
    body_data = json.loads(request.body)
    chats = Chat.objects.by_user(request.user).search(body_data['query'])

    return TemplateResponse(
        request,
        'django_spire/ai/chat/widget/search_chat_results_widget.html',
        {
            'search_results': [
                {
                    'name': chat.name,
                    'id': chat.id,
                } for chat in chats
            ]
        }
    )