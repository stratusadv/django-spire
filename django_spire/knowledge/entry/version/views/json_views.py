from __future__ import annotations

import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from django_spire.core.decorators import valid_ajax_request_required
from django_spire.core.shortcuts import get_object_or_null_obj
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

    return JsonResponse(
        {
            'type': 'success',
            'entry_version_block_json': version_block.services.transformation.to_json()
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

    version_block.services.processor.set_deleted()

    return JsonResponse({'type': 'success'})


@valid_ajax_request_required
def reorder_view(request: WSGIRequest, pk: int) -> JsonResponse:
    entry_version = get_object_or_null_obj(EntryVersion, pk=pk)

    if entry_version.id is None:
        return JsonResponse({'type': 'error', 'message': 'EntryVersion not found.'})

    body_data = json.loads(request.body.decode('utf-8'))

    order = body_data.get('order', None)

    if order is None:
        return JsonResponse({'type': 'error', 'message': 'Order Not Found.'})

    block_id = body_data.get('block_id')

    if not body_data.get('block_id'):
        return JsonResponse({'type': 'error', 'message': 'Missing Required Data.'})

    block = get_object_or_null_obj(EntryVersionBlock, pk=block_id)

    if block.id is None:
        return JsonResponse({'type': 'error', 'message': 'Block not found.'})

    block.ordering_services.processor.move_to_position(
        destination_objects=entry_version.blocks.active(),
        position=order,
    )

    return JsonResponse({
        'type': 'success', 'message': 'Order reordered successfully',
    })
