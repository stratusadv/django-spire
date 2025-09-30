from __future__ import annotations

from typing_extensions import Any, TYPE_CHECKING

from django_spire.auth.controller.controller import AppAuthController
from django_spire.conf import settings
from django_spire.consts import __VERSION__
from django_spire.theme.models import Theme
from django_spire.theme.utils import get_theme_cookie_name

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def django_spire(request: WSGIRequest) -> dict[str, Any]:
    auth_controller_dict = {}

    for app_name in settings.DJANGO_SPIRE_AUTH_CONTROLLERS:
        auth_controller_dict[app_name] = AppAuthController(app_name, request=request)

    return {
        'DJANGO_SPIRE_VERSION': __VERSION__,
        'AuthController': auth_controller_dict
    }


def theme_context(request: WSGIRequest) -> dict[str, Any]:
    default_string = getattr(
        settings,
        'DJANGO_SPIRE_DEFAULT_THEME',
        'default-light'
    )

    default = Theme.from_string(
        default_string,
        default=Theme.get_default()
    )

    name = get_theme_cookie_name()
    cookie = request.COOKIES.get(name, '')
    theme = Theme.from_string(cookie, default=default)

    path = getattr(
        settings,
        'DJANGO_SPIRE_THEME_PATH',
        '/static/django_spire/css/themes/{family}/app-{mode}.css'
    )

    return {
        'DJANGO_SPIRE_DEFAULT_THEME': default.value,
        'DJANGO_SPIRE_THEME_COOKIE_NAME': name,
        'DJANGO_SPIRE_THEME_PATH': path,
        'theme': theme.to_dict(),
    }
