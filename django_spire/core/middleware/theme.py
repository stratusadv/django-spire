from __future__ import annotations

from typing_extensions import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponse


class ThemeMiddleware:
    def __init__(self, get_response: Callable[[WSGIRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: WSGIRequest) -> HttpResponse:
        theme = request.COOKIES.get('django-spire-theme', 'rose-pine-light')

        parts = theme.split('-')
        mode = parts[-1]
        family = '-'.join(parts[:-1])

        request.theme = {
            'full': theme,
            'family': family,
            'mode': mode,
            'is_dark': mode == 'dark',
            'css_path': f'django_spire/css/themes/{family}/app-{mode}.css'
        }

        return self.get_response(request)
