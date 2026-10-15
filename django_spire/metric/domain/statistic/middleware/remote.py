from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

import requests
from django.conf import settings

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

_EXCLUDED_PATHS = ('/admin/', '/api/')

_RECORD_API_PATH = 'api/v1/metric/domain/statistic'
_RECORD_TIMEOUT = 10
_WORKER_NAME = 'django-spire-remote-statistic-click'


class RemoteClickMiddleware:
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

        if request.path.startswith(_EXCLUDED_PATHS):
            return False

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return False

        return 'text/html' in response.get('Content-Type', '')

    def _dispatch_click(self, request: HttpRequest) -> None:
        statistic_key = getattr(settings, 'DJANGO_SPIRE_METRIC_STATISTIC_KEY', '')
        sub_domain_key = getattr(settings, 'DJANGO_SPIRE_METRIC_SUB_DOMAIN_KEY', '')
        base_url = getattr(settings, 'DJANGO_SPIRE_REMOTE_API_URL', '')
        api_key = getattr(settings, 'DJANGO_SPIRE_REMOTE_API_KEY', '')

        if not (statistic_key and sub_domain_key and base_url and api_key):
            return

        reference = self._get_reference(request)

        if self.threaded:
            thread = threading.Thread(
                target=self._record_click,
                args=(base_url, api_key, statistic_key, sub_domain_key, reference),
                daemon=True,
                name=_WORKER_NAME,
            )
            thread.start()
        else:
            self._record_click(base_url, api_key, statistic_key, sub_domain_key, reference)

    @staticmethod
    def _get_reference(request: HttpRequest) -> str:
        resolver_match = getattr(request, 'resolver_match', None)
        view_name = getattr(resolver_match, 'view_name', None)
        return view_name or request.path

    @staticmethod
    def _record_click(
        base_url: str, api_key: str, statistic_key: str, sub_domain_key: str, reference: str
    ) -> None:
        url = f'{base_url.rstrip("/")}/{_RECORD_API_PATH}/{statistic_key}/record'
        headers = {'X-API-Key': api_key, 'Content-Type': 'application/json'}
        payload = {'reference': reference, 'sub_domain_key': sub_domain_key, 'value': '1'}

        try:
            response = requests.request(
                method='POST', url=url, headers=headers, json=payload, timeout=_RECORD_TIMEOUT
            )
            response.raise_for_status()
        except requests.RequestException:
            logger.debug('Remote statistic click record failed for %r', reference, exc_info=True)
