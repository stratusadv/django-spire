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
        return JsonResponse({'response': 'Chat does not exist. Refresh and try again.'})

    chat.set_deleted()

    return JsonResponse({'type': 'success', 'message': 'Chat deleted.'})


def workflow_process_view(request: WSGIRequest) -> JsonResponse:
    body = json.loads(request.body.decode('utf-8'))
    return JsonResponse({'response': chat_workflow_process(request, body)})
