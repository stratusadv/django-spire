from __future__ import annotations

import json

from http import HTTPStatus
from typing_extensions import TYPE_CHECKING

from django.http import JsonResponse
from django.views.decorators.http import require_POST

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@require_POST
def set_theme(request: WSGIRequest) -> JsonResponse:
    try:
        data = json.loads(request.body)
        theme = data.get('theme')

        if not theme:
            return JsonResponse(
                {'success': False, 'error': 'Theme is required'},
                status=HTTPStatus.BAD_REQUEST
            )

        response = JsonResponse({'success': True})

        response.set_cookie(
            'project-theme',
            theme,
            max_age=31536000
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'error': 'Invalid JSON'},
            status=HTTPStatus.BAD_REQUEST
        )
    except Exception:
        return JsonResponse(
            {'success': False, 'error': 'Server error'},
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )
    else:
        return response
