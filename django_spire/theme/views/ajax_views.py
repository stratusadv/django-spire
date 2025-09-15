from __future__ import annotations

import json

from http import HTTPStatus
from typing_extensions import TYPE_CHECKING

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django_spire.theme.models import Theme

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@require_POST
def set_theme(request: WSGIRequest) -> JsonResponse:
    data = json.loads(request.body)
    theme = data.get('theme')

    if not theme:
        return JsonResponse(
            {'error': 'Theme is required', 'success': False},
            status=HTTPStatus.BAD_REQUEST
        )

    validated = Theme.from_string(theme, default=None)

    if not validated:
        return JsonResponse(
            {'error': f'Invalid theme: {theme}', 'success': False},
            status=HTTPStatus.BAD_REQUEST
        )

    response = JsonResponse({
        'success': True,
        'theme': validated.to_dict()
    })

    response.set_cookie(
        'app-theme',
        validated.value,
        max_age=31536000
    )

    return response
