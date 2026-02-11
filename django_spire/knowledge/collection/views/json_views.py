from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.http import JsonResponse

from django_spire.contrib.responses.json_response import (
    error_json_response,
    success_json_response,
)
from django_spire.core.decorators import valid_ajax_request_required
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.knowledge.collection.models import Collection


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@valid_ajax_request_required
def reorder_view(request: WSGIRequest) -> JsonResponse:
    body_data = json.loads(request.body.decode('utf-8'))

    collection_id = body_data.get('collection_id', 0)
    collection = get_object_or_null_obj(Collection, pk=collection_id)

    if not collection.id:
        return error_json_response('Collection not found.')

    order = body_data.get('order', None)
    if order is None:
        return error_json_response('Order must be provided.')

    collection.services.ordering.reorder(
        order=order,
        new_parent_pk=body_data.get('parent', None),
    )

    return success_json_response()
