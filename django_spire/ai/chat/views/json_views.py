import json

from django.http import JsonResponse

from django_spire.ai.chat.tools import chat_workflow_process

def chat_workflow_process_json_view(request) -> JsonResponse:
    body = json.loads(request.body.decode('utf-8'))

    response = chat_workflow_process(
        request,
        body
    )

    return JsonResponse({
        'response': response
    })