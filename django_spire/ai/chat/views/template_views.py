import json

from django.template.response import TemplateResponse

from django_spire.ai.chat.models import Chat


def load_template_view(request):
    body_data = json.loads(request.body)

    print(body_data)

    chat, created = Chat.objects.get_or_create(
        id=body_data['chat_id'] if body_data['chat_id'] != 0 else None,
        user=request.user,
    )

    if created:
        chat.name = 'New Chat'
        chat.save()

    return TemplateResponse(
        request,
        'spire/ai/chat/widget/chat_dialog_widget.html',
        {
            'chat': chat,
            'height_correction': body_data['height_correction']
        }
    )

def recent_template_view(request):
    chats = (
        Chat.objects
        .by_user(request.user)
        .order_by('-last_message_datetime')
    )[:10]

    return TemplateResponse(
        request,
        'spire/ai/chat/widget/chat_recent_list_widget.html',
        {
            'recent_chats': [
                {
                    'name': chat.name,
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
        'spire/ai/chat/widget/chat_search_results_widget.html',
        {
            'search_results': [
                {
                    'name': chat.name,
                } for chat in chats
            ]
        }
    )