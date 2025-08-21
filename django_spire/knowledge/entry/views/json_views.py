from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.core.decorators import valid_ajax_request_required
from django_spire.knowledge.entry.models import Entry
from django.http import JsonResponse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@valid_ajax_request_required
def update_files_view(request: WSGIRequest) -> JsonResponse:
    return JsonResponse({'files_json': Entry.services.tool.get_files_to_convert_json()})
