from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.http import JsonResponse
from django.views.decorators.http import require_POST

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@require_POST
def set_theme(request: WSGIRequest) -> JsonResponse:
    theme = request.POST.get('theme')
    response = JsonResponse({'success': True})

    response.set_cookie(
        'django-spire-theme',
        theme,
        max_age=31536000
    )

    return response
