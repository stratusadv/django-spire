from __future__ import annotations

import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from django_spire.auth.controller.controller import AppAuthController
from django_spire.core.decorators import valid_ajax_request_required
from django_spire.knowledge.entry.version.models import EntryVersion


@valid_ajax_request_required
@AppAuthController('knowledge').permission_required('can_change')
def update_blocks_view(request: WSGIRequest, pk: int) -> JsonResponse:
    entry_version = get_object_or_404(EntryVersion.objects.prefetch_blocks(), pk=pk)

    block_data_list = json.loads(request.body.decode('utf-8'))

    entry_version.services.processor.add_update_delete_blocks(block_data_list)

    return JsonResponse({'type': 'success'})
