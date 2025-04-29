from __future__ import annotations

import json

from typing import TYPE_CHECKING
from django.http import JsonResponse

from django_spire.ai.chat.models import Chat
from django_spire.ai.chat.tools import chat_workflow_process

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def delete_view(request: WSGIRequest, pk: int) -> JsonResponse:
    try:
        chat = Chat.objects.get(pk=pk)
    except Chat.DoesNotExist:
        return JsonResponse(
            {
                'type': 'error',
                'message': 'Chat does not exist. Refresh and try again.'
            }
        )

    chat.set_deleted()

    return JsonResponse({'type': 'success', 'message': 'Chat deleted.'})


def rename_view(request: WSGIRequest, pk: int) -> JsonResponse:
    try:
        chat = Chat.objects.get(pk=pk)
    except Chat.DoesNotExist:
        return JsonResponse(
            {
                'type': 'error',
                'message': 'Chat does not exist. Refresh and try again.'
            }
        )

    new_chat_name = json.loads(request.body.decode("utf-8")).get('new_name', '')

    if new_chat_name == '' or len(new_chat_name) > 128:
        return JsonResponse({'type': 'error', 'message': 'Chat name was not updated.'})

    chat.name = new_chat_name
    chat.save()

    return JsonResponse({'type': 'success'})


def workflow_process_view(request: WSGIRequest) -> JsonResponse:
    body = json.loads(request.body.decode('utf-8'))
    return JsonResponse({'response': chat_workflow_process(request, body)})
