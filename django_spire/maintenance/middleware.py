from __future__ import annotations

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.MAINTENANCE_MODE and 'maintenance/mode' not in request.path:
            url = reverse('home:maintenance_mode') + f'?next={request.path}'
            return HttpResponseRedirect(url)

        return self.get_response(request)
