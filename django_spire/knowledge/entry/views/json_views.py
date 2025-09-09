from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.core.decorators import valid_ajax_request_required
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.models import Entry
from django.http import JsonResponse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@valid_ajax_request_required
def reorder_view(request: WSGIRequest) -> JsonResponse:
    body_data = json.loads(request.body.decode('utf-8'))

    entry_id = body_data.get('entry_id', 0)
    entry = get_object_or_null_obj(Entry, pk=entry_id)

    if entry.id is None:
        return JsonResponse({'type': 'error', 'message': 'Entry not found.'})

    order = body_data.get('order', None)

    if order is None:
        return JsonResponse({'type': 'error', 'message': 'Order not found.'})

    collection_id = body_data.get('collection_id', None)
    collection = get_object_or_null_obj(Collection, pk=collection_id)

    if collection.id is None:
        return JsonResponse({'type': 'error', 'message': 'Collection not found.'})

    entry.collection = collection
    entry.save()

    entry.ordering_services.processor.move_to_position(
        destination_objects=entry.collection.entries.active(),
        position=order,
    )

    return JsonResponse({'type': 'success', 'message': 'Order reordered successfully'})


@valid_ajax_request_required
def update_files_view(request: WSGIRequest) -> JsonResponse:
    return JsonResponse({'files_json': Entry.services.tool.get_files_to_convert_json()})
