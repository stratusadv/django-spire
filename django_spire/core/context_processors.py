from __future__ import annotations

from django_spire.conf import settings
from typing_extensions import TYPE_CHECKING, Any

from django_spire.auth.controller.controller import AppAuthController
from django_spire.consts import __VERSION__

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def django_spire(request: WSGIRequest) -> dict[str, Any]:
    auth_controller_dict = {}
    for app_name, object_module_path in settings.DJANGO_SPIRE_AUTH_CONTROLLERS.items():
        auth_controller_dict[app_name] = AppAuthController(app_name, request=request)

    return {
        'DJANGO_SPIRE_VERSION': __VERSION__,
        'app_bootstrap_icon': {
            'help_desk': 'bi bi-headset'
        },
        'AuthController': auth_controller_dict
    }
