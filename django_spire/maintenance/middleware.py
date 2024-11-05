from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: WSGIRequest):
        if settings.MAINTENANCE_MODE and 'maintenance/mode' not in request.path:
            url = reverse('home:maintenance_mode') + f'?next={request.path}'
            return HttpResponseRedirect(url)

        return self.get_response(request)
