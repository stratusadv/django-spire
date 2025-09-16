from __future__ import annotations

import json

from http import HTTPStatus
from typing_extensions import TYPE_CHECKING

from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET, require_POST

from django_spire.theme.enums import ThemeFamily, ThemeMode
from django_spire.theme.models import Theme
from django_spire.theme.utils import get_theme_cookie_name

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@cache_page(60 * 60 * 24)
@require_GET
def get_config(request: WSGIRequest) -> JsonResponse:
    config = {
        'families': {},
        'default_family': Theme.DEFAULT_FAMILY.value,
        'default_mode': Theme.DEFAULT_MODE.value,
        'separator': Theme.SEPARATOR,
        'cookie_name': get_theme_cookie_name()
    }

    for family in ThemeFamily:
        config['families'][family.value] = {
            'name': Theme.FAMILY_DISPLAY_NAMES.get(family, family.value),
            'modes': [mode.value for mode in ThemeMode]
        }

    return JsonResponse({
        'success': True,
        'data': config
    })


@require_POST
def set_theme(request: WSGIRequest) -> JsonResponse:
    data = json.loads(request.body)
    theme = data.get('theme')

    if not theme:
        return JsonResponse(
            {'error': 'Theme is required', 'success': False},
            status=HTTPStatus.BAD_REQUEST
        )

    try:
        validated = Theme.from_string(theme)
    except ValueError:
        return JsonResponse(
            {'error': f'Invalid theme: {theme}', 'success': False},
            status=HTTPStatus.BAD_REQUEST
        )

    response = JsonResponse({
        'success': True,
        'theme': validated.to_dict()
    })

    response.set_cookie(
        get_theme_cookie_name(),
        validated.value,
        max_age=31536000
    )

    return response
