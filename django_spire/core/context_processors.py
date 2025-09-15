from __future__ import annotations

import json

from typing_extensions import Any, TYPE_CHECKING

from django_spire.auth.controller.controller import AppAuthController
from django_spire.conf import settings
from django_spire.consts import __VERSION__
from django_spire.theme.enums import ThemeFamily, ThemeMode
from django_spire.theme.models import Theme

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
    default_string = getattr(settings, 'DJANGO_SPIRE_DEFAULT_THEME', 'default-light')

    default = Theme.from_string(
        default_string,
        default=Theme.get_default()
    )

    cookie = request.COOKIES.get('app-theme', '')
    theme = Theme.from_string(cookie, default=default)

    config = {
        'families': {},
        'default_family': Theme.DEFAULT_FAMILY.value,
        'default_mode': Theme.DEFAULT_MODE.value,
        'separator': Theme.SEPARATOR
    }

    for family in ThemeFamily:
        config['families'][family.value] = {
            'name': Theme.FAMILY_DISPLAY_NAMES.get(family, family.value),
            'modes': [mode.value for mode in ThemeMode]
        }

    return {
        'DJANGO_SPIRE_DEFAULT_THEME': default.value,
        'DJANGO_SPIRE_THEME_PATH': settings.DJANGO_SPIRE_THEME_PATH,
        'theme': theme.to_dict(),
        'theme_config': json.dumps(config),
    }
