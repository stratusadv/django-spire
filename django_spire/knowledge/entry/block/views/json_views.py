import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from django_spire.core.decorators import valid_ajax_request_required
from django_spire.knowledge.entry.block.models import EntryVersionBlock


@valid_ajax_request_required
def update_text_view(request: WSGIRequest, pk: int) -> JsonResponse:
    try:
        version_block = EntryVersionBlock.objects.get(pk=pk)
    except EntryVersionBlock.DoesNotExist:
        return JsonResponse({'type': 'error', 'message': 'Block Not Found'})

    body_data = json.loads(request.body.decode('utf-8'))
    value = body_data.get('value')
    block_type = body_data.get('block_type')

    if value is None or not block_type:
        return JsonResponse({'type': 'error', 'message': 'Missing Required Data'})

    version_block.services.processor.update(value=value, block_type=block_type)

    return JsonResponse({'type': 'success'})
