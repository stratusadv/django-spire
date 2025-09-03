import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from django_spire.core.decorators import valid_ajax_request_required
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
from django_spire.knowledge.entry.version.models import EntryVersion


@valid_ajax_request_required
def create_blank_block_view(request: WSGIRequest, pk: int) -> JsonResponse:
    entry_version = EntryVersion.objects.get(pk=pk)

    body_data = json.loads(request.body.decode('utf-8'))

    if 'order' not in body_data or 'block_type' not in body_data:
        return JsonResponse({'type': 'error', 'message': 'Missing Required Data.'})

    block_type = body_data.pop('block_type')
    order = body_data.pop('order')

    version_block = EntryVersionBlock.services.factory.create_blank_block(
        entry_version=entry_version,
        block_type=block_type,
        order=order,
        **body_data,
    )
    entry_version.services.processor.insert_block(version_block=version_block)

    return JsonResponse(
        {
            'type': 'success',
            'entry_version_block_json': json.dumps(
                version_block.services.transformation.to_dict()
            )
        }
    )


@valid_ajax_request_required
def delete_block_view(request: WSGIRequest, pk: int) -> JsonResponse:
    entry_version = EntryVersion.objects.get(pk=pk)

    body_data = json.loads(request.body.decode('utf-8'))
    version_block_pk = body_data.get('version_block_pk')

    try:
        version_block = EntryVersionBlock.objects.get(pk=version_block_pk)
    except EntryVersionBlock.DoesNotExist:
        return JsonResponse({'type': 'error', 'message': 'Block Not Found.'})

    entry_version.services.processor.delete_block(version_block=version_block)

    return JsonResponse({'type': 'success'})
