import json

from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from django_spire.core.decorators import valid_ajax_request_required
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.knowledge.collection.models import Collection


@valid_ajax_request_required
def reorder_view(request: WSGIRequest, pk: int) -> JsonResponse:
    collection = get_object_or_null_obj(Collection, pk=pk)

    if not collection.id:
        return JsonResponse({'type': 'error', 'message': 'Collection not found.'})

    body_data = json.loads(request.body.decode('utf-8'))

    order = body_data.get('order', None)
    if order is None:
        return JsonResponse({'type': 'error', 'message': 'Order must be provided.'})

    collection.services.ordering.reorder(
        order=order,
        new_parent_pk=body_data.get('parent', None),
    )

    return JsonResponse({'type': 'success'})
