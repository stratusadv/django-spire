from __future__ import annotations

import threading
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import requests
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, override_settings
from requests import HTTPError

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.middleware import RemoteClickMiddleware
from django_spire.metric.domain.statistic.middleware.remote import _WORKER_NAME
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
)

_REMOTE_URL = 'https://metrics.example.com'
_REMOTE_KEY = 'secret-api-key'


class RemoteClickMiddlewareTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def _remote_settings(self, **overrides) -> override_settings:
        values = {
            'DJANGO_SPIRE_METRIC_STATISTIC_KEY': str(self.statistic.key),
            'DJANGO_SPIRE_METRIC_SUB_DOMAIN_KEY': str(self.sub_domain.key),
            'DJANGO_SPIRE_REMOTE_API_URL': _REMOTE_URL,
            'DJANGO_SPIRE_REMOTE_API_KEY': _REMOTE_KEY,
        }
        values.update(overrides)
        return override_settings(**values)

    def _run(
        self, request: HttpRequest, response: HttpResponse, *, threaded: bool = False
    ) -> HttpResponse:
        def view(_request: HttpRequest) -> HttpResponse:
            return response

        return RemoteClickMiddleware(view, threaded=threaded)(request)

    @staticmethod
    def _ok_response() -> MagicMock:
        return MagicMock()

    def _assert_not_posted(self, request: HttpRequest, response: HttpResponse) -> None:
        with self._remote_settings(), patch('requests.request') as mock_request:
            self._run(request, response)

        mock_request.assert_not_called()

    def test_get_html_page_posts_click(self) -> None:
        request = RequestFactory().get('/some/path/')
        request.resolver_match = SimpleNamespace(view_name='app:page:detail')
        response = HttpResponse(content_type='text/html')

        with self._remote_settings(), patch('requests.request') as mock_request:
            mock_request.return_value = self._ok_response()
            self._run(request, response)

        mock_request.assert_called_once()
        kwargs = mock_request.call_args.kwargs
        assert kwargs['method'] == 'POST'
        assert (
            kwargs['url']
            == f'{_REMOTE_URL}/api/v1/metric/domain/statistic/{self.statistic.key}/record'
        )
        assert kwargs['headers'] == {'X-API-Key': _REMOTE_KEY, 'Content-Type': 'application/json'}
        assert kwargs['json'] == {
            'reference': 'app:page:detail',
            'sub_domain_key': str(self.sub_domain.key),
            'value': '1',
        }
        assert kwargs['timeout'] == 10

    def test_reference_falls_back_to_path(self) -> None:
        request = RequestFactory().get('/some/other/path/')
        response = HttpResponse(content_type='text/html')

        with self._remote_settings(), patch('requests.request') as mock_request:
            mock_request.return_value = self._ok_response()
            self._run(request, response)

        assert mock_request.call_args.kwargs['json']['reference'] == '/some/other/path/'

    def test_trailing_slash_base_url_is_normalized(self) -> None:
        request = RequestFactory().get('/some/path/')
        response = HttpResponse(content_type='text/html')

        with (
            self._remote_settings(DJANGO_SPIRE_REMOTE_API_URL=f'{_REMOTE_URL}/'),
            patch('requests.request') as mock_request,
        ):
            mock_request.return_value = self._ok_response()
            self._run(request, response)

        assert (
            mock_request.call_args.kwargs['url']
            == f'{_REMOTE_URL}/api/v1/metric/domain/statistic/{self.statistic.key}/record'
        )

    def test_unconfigured_settings_are_noop(self) -> None:
        blanks = {
            'DJANGO_SPIRE_METRIC_STATISTIC_KEY': '',
            'DJANGO_SPIRE_METRIC_SUB_DOMAIN_KEY': '',
            'DJANGO_SPIRE_REMOTE_API_URL': '',
            'DJANGO_SPIRE_REMOTE_API_KEY': '',
        }

        for setting_name, blank in blanks.items():
            with self.subTest(setting=setting_name):
                request = RequestFactory().get('/some/path/')
                response = HttpResponse(content_type='text/html')

                with (
                    self._remote_settings(**{setting_name: blank}),
                    patch('requests.request') as mock_request,
                ):
                    self._run(request, response)

                mock_request.assert_not_called()

    def test_post_request_is_not_tracked(self) -> None:
        request = RequestFactory().post('/some/path/')
        response = HttpResponse(content_type='text/html')

        self._assert_not_posted(request, response)

    def test_non_200_response_is_not_tracked(self) -> None:
        request = RequestFactory().get('/some/path/')
        response = HttpResponse(content_type='text/html', status=404)

        self._assert_not_posted(request, response)

    def test_non_html_response_is_not_tracked(self) -> None:
        request = RequestFactory().get('/some/path/')
        response = HttpResponse('{}', content_type='application/json')

        self._assert_not_posted(request, response)

    def test_admin_path_is_not_tracked(self) -> None:
        request = RequestFactory().get('/admin/')
        response = HttpResponse(content_type='text/html')

        self._assert_not_posted(request, response)

    def test_api_path_is_not_tracked(self) -> None:
        request = RequestFactory().get('/api/v1/')
        response = HttpResponse(content_type='text/html')

        self._assert_not_posted(request, response)

    def test_xhr_request_is_not_tracked(self) -> None:
        request = RequestFactory().get('/some/path/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = HttpResponse(content_type='text/html')

        self._assert_not_posted(request, response)

    def test_threaded_mode_posts_from_background_thread(self) -> None:
        request = RequestFactory().get('/some/path/')
        response = HttpResponse(content_type='text/html')
        posted = threading.Event()
        thread_names: list[str] = []
        payloads: list[tuple[str, str, dict | None]] = []

        def fake_request(method: str, url: str, **kwargs) -> MagicMock:
            thread_names.append(threading.current_thread().name)
            payloads.append((method, url, kwargs.get('json')))
            posted.set()
            return self._ok_response()

        with self._remote_settings(), patch('requests.request', side_effect=fake_request):
            self._run(request, response, threaded=True)

        assert posted.wait(timeout=5)
        assert thread_names == [_WORKER_NAME]
        assert payloads == [
            (
                'POST',
                f'{_REMOTE_URL}/api/v1/metric/domain/statistic/{self.statistic.key}/record',
                {
                    'reference': '/some/path/',
                    'sub_domain_key': str(self.sub_domain.key),
                    'value': '1',
                },
            )
        ]

    def test_request_failure_is_swallowed(self) -> None:
        request = RequestFactory().get('/some/path/')
        response = HttpResponse(content_type='text/html')

        with (
            self._remote_settings(),
            patch(
                'requests.request',
                side_effect=requests.exceptions.ConnectionError('connection refused'),
            ),
        ):
            result = self._run(request, response)

        assert result.status_code == 200

    def test_http_error_is_swallowed(self) -> None:
        request = RequestFactory().get('/some/path/')
        response = HttpResponse(content_type='text/html')
        mock_response = self._ok_response()
        mock_response.raise_for_status.side_effect = HTTPError('500 Server Error')

        with self._remote_settings(), patch('requests.request', return_value=mock_response):
            result = self._run(request, response)

        assert result.status_code == 200
