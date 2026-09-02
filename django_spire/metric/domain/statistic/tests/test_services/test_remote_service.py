from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import override_settings
from requests import HTTPError

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.models import Statistic
from django_spire.metric.domain.statistic.services.service import StatisticService
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
)

_REMOTE_URL = 'https://metrics.example.com'
_REMOTE_KEY = 'secret-api-key'


class StatisticRemoteRecordServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def _mock_response(self, payload: dict) -> MagicMock:
        response = MagicMock()
        response.json.return_value = payload
        return response

    @override_settings(
        DJANGO_SPIRE_REMOTE_API_URL=_REMOTE_URL, DJANGO_SPIRE_REMOTE_API_KEY=_REMOTE_KEY
    )
    @patch('requests.request')
    def test_remote_record_posts_to_endpoint(self, mock_request: MagicMock):
        mock_request.return_value = self._mock_response({'value': '5'})

        result = StatisticService.remote_record(
            self.statistic.key, self.sub_domain.key, '/home/', value=Decimal(5)
        )

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs['method'] == 'POST'
        assert (
            call_kwargs['url']
            == f'{_REMOTE_URL}/api/v1/metric/domain/statistic/{self.statistic.key}/record'
        )
        assert call_kwargs['headers']['X-API-Key'] == _REMOTE_KEY
        assert call_kwargs['json'] == {
            'reference': '/home/',
            'sub_domain_key': self.sub_domain.key,
            'value': '5',
        }
        assert result == {'value': '5'}

    @patch('requests.request')
    def test_remote_record_unconfigured_returns_none(self, mock_request: MagicMock):
        result = StatisticService.remote_record(self.statistic.key, self.sub_domain.key, '/home/')

        assert result is None
        mock_request.assert_not_called()

    @override_settings(
        DJANGO_SPIRE_REMOTE_API_URL=_REMOTE_URL, DJANGO_SPIRE_REMOTE_API_KEY=_REMOTE_KEY
    )
    @patch('requests.request')
    def test_remote_record_http_error_returns_none(self, mock_request: MagicMock):
        response = self._mock_response({})
        response.raise_for_status.side_effect = HTTPError('500 Server Error')
        mock_request.return_value = response

        result = StatisticService.remote_record(self.statistic.key, self.sub_domain.key, '/home/')

        assert result is None

    @override_settings(
        DJANGO_SPIRE_REMOTE_API_URL=_REMOTE_URL, DJANGO_SPIRE_REMOTE_API_KEY=_REMOTE_KEY
    )
    @patch('requests.request')
    def test_remote_record_model_classmethod_delegates(self, mock_request: MagicMock):
        mock_request.return_value = self._mock_response({'value': '1'})

        result = Statistic.remote_record(self.statistic.key, self.sub_domain.key, '/home/')

        assert result == {'value': '1'}
        mock_request.assert_called_once()
