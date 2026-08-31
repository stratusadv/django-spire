from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.middleware import StatisticClickMiddleware
from django_spire.metric.domain.statistic.models import StatisticValue
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
)


class StatisticClickMiddlewareTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def _tracking_settings(self) -> override_settings:
        return override_settings(
            DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY=str(self.statistic.key),
            DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY=str(self.sub_domain.key),
        )

    def _run(
        self, request: HttpRequest, response: HttpResponse, *, threaded: bool = False
    ) -> HttpResponse:
        def view(_request: HttpRequest) -> HttpResponse:
            return response

        return StatisticClickMiddleware(view, threaded=threaded)(request)

    def test_get_html_page_tracks_click(self) -> None:
        request = RequestFactory().get('/metric/domain/statistic/page/1/detail/')
        request.resolver_match = SimpleNamespace(
            view_name='django_spire:metric:domain:statistic:page:detail'
        )
        response = HttpResponse(content_type='text/html')

        with self._tracking_settings():
            self._run(request, response)

        value = StatisticValue.objects.latest('pk')
        assert value.statistic == self.statistic
        assert value.sub_domain == self.sub_domain
        assert value.reference == 'django_spire:metric:domain:statistic:page:detail'

    def test_post_is_not_tracked(self) -> None:
        request = RequestFactory().post('/metric/domain/statistic/page/1/detail/')
        response = HttpResponse(content_type='text/html')

        with self._tracking_settings():
            self._run(request, response)

        assert not StatisticValue.objects.exists()

    def test_non_200_response_is_not_tracked(self) -> None:
        request = RequestFactory().get('/some/path/')
        response = HttpResponse(content_type='text/html', status=404)

        with self._tracking_settings():
            self._run(request, response)

        assert not StatisticValue.objects.exists()

    def test_non_html_response_is_not_tracked(self) -> None:
        request = RequestFactory().get('/some/path/')
        response = HttpResponse('{}', content_type='application/json')

        with self._tracking_settings():
            self._run(request, response)

        assert not StatisticValue.objects.exists()

    def test_admin_path_is_not_tracked(self) -> None:
        request = RequestFactory().get('/admin/')
        response = HttpResponse(content_type='text/html')

        with self._tracking_settings():
            self._run(request, response)

        assert not StatisticValue.objects.exists()

    def test_api_path_is_not_tracked(self) -> None:
        request = RequestFactory().get('/api/v1/')
        response = HttpResponse(content_type='text/html')

        with self._tracking_settings():
            self._run(request, response)

        assert not StatisticValue.objects.exists()

    def test_xhr_request_is_not_tracked(self) -> None:
        request = RequestFactory().get('/some/path/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = HttpResponse(content_type='text/html')

        with self._tracking_settings():
            self._run(request, response)

        assert not StatisticValue.objects.exists()

    def test_noop_when_not_configured(self) -> None:
        request = RequestFactory().get('/some/path/')
        response = HttpResponse(content_type='text/html')

        self._run(request, response)

        assert not StatisticValue.objects.exists()

    def test_threaded_mode_enqueues_reference(self) -> None:
        request = RequestFactory().get('/some/path/')
        request.resolver_match = SimpleNamespace(view_name='django_spire:metric:page:detail')
        response = HttpResponse(content_type='text/html')

        with (
            self._tracking_settings(),
            patch(
                'django_spire.metric.domain.statistic.middleware.tracking_queue.enqueue'
            ) as enqueue_mock,
        ):
            self._run(request, response, threaded=True)

        enqueue_mock.assert_called_once_with('django_spire:metric:page:detail')

    def test_sync_mode_writes_immediately(self) -> None:
        request = RequestFactory().get('/some/path/')
        request.resolver_match = SimpleNamespace(view_name='django_spire:metric:page:detail')
        response = HttpResponse(content_type='text/html')

        with self._tracking_settings():
            self._run(request, response, threaded=False)

        value = StatisticValue.objects.latest('pk')
        assert value.reference == 'django_spire:metric:page:detail'
