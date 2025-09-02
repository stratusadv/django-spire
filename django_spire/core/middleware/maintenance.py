from __future__ import annotations

from django.conf import settings
from django.template.response import TemplateResponse
from typing_extensions import TYPE_CHECKING

from django_spire.consts import MAINTENANCE_MODE_SETTINGS_NAME

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: WSGIRequest):
        # maintenance_mode = getattr(settings, MAINTENANCE_MODE_SETTINGS_NAME)

        # if maintenance_mode is None:
        #     raise ValueError(f'"{MAINTENANCE_MODE_SETTINGS_NAME}" must be set in the django settings.')

        # if maintenance_mode:
        #     return TemplateResponse(
        #         request=request,
        #         template='django_spire/page/maintenance_page.html',
        #     )

        return self.get_response(request)
