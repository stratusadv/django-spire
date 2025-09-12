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
    default_theme = getattr(settings, 'DJANGO_SPIRE_DEFAULT_THEME', 'standard-light')

    parts = default_theme.split('-')
    default_mode = parts[-1]
    default_family = '-'.join(parts[:-1])

    return {
        'theme': getattr(request, 'theme', {
            'full': default_theme,
            'family': default_family,
            'mode': default_mode,
            'is_dark': default_mode == 'dark',
            'stylesheet': f'django_spire/css/themes/{default_family}/app-{default_mode}.css'
        }),
        'DJANGO_SPIRE_DEFAULT_THEME': default_theme
    }
