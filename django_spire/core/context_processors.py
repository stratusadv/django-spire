from __future__ import annotations

from typing import Any, TYPE_CHECKING

from django_spire.auth.controller.controller import AppAuthController
from django_spire.conf import settings
from django_spire.constants import __VERSION__

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


THEME_COOKIE_NAME = 'django_spire-theme-mode'


def django_spire(request: WSGIRequest) -> dict[str, Any]:
    auth_controller_dict = {}

    for app_name in settings.DJANGO_SPIRE_AUTH_CONTROLLERS:
        auth_controller_dict[app_name] = AppAuthController(app_name, request=request)

    return {'DJANGO_SPIRE_VERSION': __VERSION__, 'AuthController': auth_controller_dict}


def theme_context(request: WSGIRequest) -> dict[str, Any]:
    default_mode = getattr(settings, 'DJANGO_SPIRE_DEFAULT_THEME_MODE', 'light')

    mode = request.COOKIES.get(THEME_COOKIE_NAME, default_mode)

    return {'DJANGO_SPIRE_THEME_COOKIE_NAME': THEME_COOKIE_NAME, 'DJANGO_SPIRE_THEME_MODE': mode}


def get_theme_cookie_name() -> str:
    return THEME_COOKIE_NAME
