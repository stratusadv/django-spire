from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from django.db import connections

from django_spire.conf import settings
from django_spire.metric.domain.statistic.services.tracking_service import StatisticTrackingService

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest, HttpResponse

_ADMIN_PATHS = ('/admin/',)
_API_PATHS = ('/api/',)


def _track_click_in_background(reference: str) -> None:
    try:
        StatisticTrackingService.track_configured(reference=reference)
    finally:
        connections.close_all()


class StatisticClickMiddleware:
    def __init__(
        self, get_response: Callable[[HttpRequest], HttpResponse], *, threaded: bool = True
    ) -> None:
        self.get_response = get_response
        self.threaded = threaded

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        if self._should_track(request, response):
            self._dispatch_click(request)

        return response

    def _should_track(self, request: HttpRequest, response: HttpResponse) -> bool:
        if request.method != 'GET':
            return False

        if response.status_code != 200:
            return False

        if request.path.startswith(_ADMIN_PATHS) or request.path.startswith(_API_PATHS):
            return False

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return False

        return 'text/html' in response.get('Content-Type', '')

    def _dispatch_click(self, request: HttpRequest) -> None:
        if not settings.DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY:
            return

        if not settings.DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY:
            return

        resolver_match = getattr(request, 'resolver_match', None)
        view_name = getattr(resolver_match, 'view_name', None)
        reference = view_name or request.path

        if self.threaded:
            thread = threading.Thread(
                target=_track_click_in_background,
                kwargs={'reference': reference},
                daemon=True,
                name='django-spire-statistic-click',
            )
            thread.start()
        else:
            StatisticTrackingService.track_configured(reference=reference)
