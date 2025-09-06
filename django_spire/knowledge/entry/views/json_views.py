from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.core.decorators import valid_ajax_request_required
from django_spire.knowledge.entry.models import Entry
from django.http import JsonResponse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@valid_ajax_request_required
def reorder_view(request: WSGIRequest, pk: int, order: int)-> JsonResponse:
    entry = get_object_or_null_obj(Entry, pk=pk)

    if entry.id is None:
        return JsonResponse({'type': 'error', 'message': 'Entry not found.'})

    all_entries = Entry.objects.active()

    entry.ordering_services.processor.move_to_position(
        destination_objects=all_entries,
        position=order,
    )

    return JsonResponse({
        'type': 'success', 'message': 'Order reordered successfully',
    })


@valid_ajax_request_required
def update_files_view(request: WSGIRequest) -> JsonResponse:
    return JsonResponse({'files_json': Entry.services.tool.get_files_to_convert_json()})
