from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from django_spire.core.shortcuts import get_object_or_null_obj

from test_project.apps.ordering import models


def reorder_view(request: WSGIRequest, pk: int, order: int)-> JsonResponse:
    duck = get_object_or_null_obj(models.Duck, pk=pk)

    if duck.id is None:
        return JsonResponse({'type': 'error', 'message': 'Duck not found'})

    all_ducks = models.Duck.objects.active().exclude(pk=pk).order_by('order')

    duck.ordering_services.processor.move_to_position(
        destination_objects=all_ducks,
        position=order,
        origin_objects=all_ducks
    )

    return JsonResponse({
        'type': 'success', 'message': 'Order reordered successfully',
    })