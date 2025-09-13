from __future__ import annotations

from typing_extensions import Any, TYPE_CHECKING

from django_spire.auth.controller.controller import AppAuthController
from django_spire.conf import settings
from django_spire.consts import __VERSION__

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def django_spire(request: WSGIRequest) -> dict[str, Any]:
    auth_controller_dict = {}

    for app_name in settings.DJANGO_SPIRE_AUTH_CONTROLLERS:
        auth_controller_dict[app_name] = AppAuthController(app_name, request=request)

    return {
        'DJANGO_SPIRE_VERSION': __VERSION__,
        'app_bootstrap_icon': {
            'help_desk': 'bi bi-headset'
        },
        'AuthController': auth_controller_dict
    }


def theme_context(request: WSGIRequest) -> dict[str, Any]:
    default_theme = settings.DJANGO_SPIRE_DEFAULT_THEME

    theme = request.COOKIES.get('app-theme', default_theme)

    parts = theme.split('-')
    mode = parts[-1]
    family = '-'.join(parts[:-1])

    return {
        'theme': {
            'full': theme,
            'family': family,
            'mode': mode,
            'is_dark': mode == 'dark',
            'stylesheet': f'django_spire/css/themes/{family}/app-{mode}.css'
        },
        'DJANGO_SPIRE_DEFAULT_THEME': default_theme
    }
