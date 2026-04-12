from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required

if TYPE_CHECKING:
    from django.http import JsonResponse
    from django.core.handlers.wsgi import WSGIRequest


@login_required
def task_info_view(request: WSGIRequest) -> JsonResponse:
    return JsonResponse({})
