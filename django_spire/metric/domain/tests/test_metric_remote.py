from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests
from django.test import SimpleTestCase, override_settings

from django_spire.contrib.rest.connector.exceptions import RestConnectorError
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.exceptions import DjangoSpireConfigurationError
from django_spire.metric import BuildSummary, Metric
from django_spire.metric.utils import _resolve_remote_target


class RemoteMetric(Metric):
    target = Metric.Target.REMOTE
    remote_target = 'central'
    domains = [
        Metric.Domain(
            'store',
            name='Store',
            subdomains=[
                Metric.SubDomain('web', name='Web'),
                Metric.SubDomain('retail', name='Retail'),
            ],
            statistic_groups=[
                Metric.StatisticGroup(
                    'orders',
                    name='Orders',
                    statistics=[Metric.Statistic('created', name='Orders created')],
                )
            ],
        )
    ]


TARGETS = {'central': {'url': 'https://metrics.example.com', 'api_key': 'secret-key'}}


class RemoteTargetResolutionTestCase(SimpleTestCase):
    def test_resolves_named_target(self):
        with override_settings(DJANGO_SPIRE_METRIC_REMOTE_TARGETS=TARGETS):
            url, api_key = _resolve_remote_target('central')
        assert url == 'https://metrics.example.com'
        assert api_key == 'secret-key'

    def test_falls_back_to_flat_settings(self):
        with override_settings(
            DJANGO_SPIRE_METRIC_REMOTE_TARGETS={},
            DJANGO_SPIRE_REMOTE_API_URL='https://fallback.example.com',
            DJANGO_SPIRE_REMOTE_API_KEY='fallback-key',
        ):
            url, api_key = _resolve_remote_target('anything')
        assert url == 'https://fallback.example.com'
        assert api_key == 'fallback-key'

    def test_raises_when_unconfigured(self):
        with (
            override_settings(
                DJANGO_SPIRE_METRIC_REMOTE_TARGETS={},
                DJANGO_SPIRE_REMOTE_API_URL='',
                DJANGO_SPIRE_REMOTE_API_KEY='',
            ),
            pytest.raises(DjangoSpireConfigurationError),
        ):
            _resolve_remote_target('central')


class RemoteRecordTestCase(BaseTestCase):
    def test_record_posts_to_remote(self):
        response = MagicMock()
        response.json.return_value = {'statistic_key': 'store__orders__created'}
        connector = MagicMock()
        connector.record.return_value = response

        with (
            override_settings(DJANGO_SPIRE_METRIC_REMOTE_TARGETS=TARGETS),
            patch(
                'django_spire.metric.metric.SpireMetricRestConnector', return_value=connector
            ) as mock_connector,
        ):
            worker = RemoteMetric.record('store', 'web', 'orders', 'created', value=2)
            worker.join()

        mock_connector.assert_called_once_with(
            base_url='https://metrics.example.com', api_key='secret-key'
        )
        connector.record.assert_called_once_with(
            'store__orders__created',
            {'reference': 'store__orders__created', 'sub_domain_key': 'store__web', 'value': '2'},
        )

    def test_record_accepts_explicit_reference(self):
        response = MagicMock()
        response.json.return_value = {}
        connector = MagicMock()
        connector.record.return_value = response

        with (
            override_settings(DJANGO_SPIRE_METRIC_REMOTE_TARGETS=TARGETS),
            patch('django_spire.metric.metric.SpireMetricRestConnector', return_value=connector),
        ):
            worker = RemoteMetric.record(
                'store', 'web', 'orders', 'created', reference='checkout', value=1
            )
            worker.join()

        connector.record.assert_called_once_with(
            'store__orders__created',
            {'reference': 'checkout', 'sub_domain_key': 'store__web', 'value': '1'},
        )

    def test_record_swallows_remote_errors(self):
        connector = MagicMock()
        connector.record.side_effect = Exception('network down')

        with (
            override_settings(DJANGO_SPIRE_METRIC_REMOTE_TARGETS=TARGETS),
            patch('django_spire.metric.metric.SpireMetricRestConnector', return_value=connector),
        ):
            worker = RemoteMetric.record('store', 'web', 'orders', 'created')
            worker.join()

        connector.record.assert_called_once_with(
            'store__orders__created',
            {'reference': 'store__orders__created', 'sub_domain_key': 'store__web', 'value': '1'},
        )


class RemoteCheckTestCase(BaseTestCase):
    def _connector(
        self, missing_sub_domains: set[str] = (), missing_statistics: set[str] = ()
    ) -> MagicMock:
        def fake_get(path: str, params: dict[str, str] | None = None) -> MagicMock:
            response = MagicMock()
            statistic_key = path.rstrip('/').rsplit('/', 2)[1]
            sub_domain_key = params.get('sub_domain_key') if params else None

            if sub_domain_key in missing_sub_domains or statistic_key in missing_statistics:
                response.status_code = 404
            else:
                response.status_code = 200
            return response

        connector = MagicMock()
        connector.get.side_effect = fake_get
        return connector

    def _check(self, connector: MagicMock) -> BuildSummary:
        with (
            override_settings(DJANGO_SPIRE_METRIC_REMOTE_TARGETS=TARGETS),
            patch('django_spire.metric.metric.SpireMetricRestConnector', return_value=connector),
        ):
            return RemoteMetric.check()

    def test_check_passes_when_reachable(self):
        summary = self._check(self._connector())
        assert summary.ok is True
        assert summary.missing == []

    def test_check_reports_missing_statistic(self):
        summary = self._check(self._connector(missing_statistics={'store__orders__created'}))
        assert summary.missing == ['store/orders/created']

    def test_check_reports_missing_sub_domain(self):
        summary = self._check(self._connector(missing_sub_domains={'store__retail'}))
        assert summary.missing == ['store/retail']

    def test_check_reports_unreachable_domain_sub_domains(self):
        summary = self._check(self._connector(missing_statistics={'store__orders__created'}))
        assert summary.missing == ['store/orders/created']
        assert any('sub-domains not checked' in error for error in summary.errors)

    def test_check_treats_connector_errors_as_missing(self):
        for error in (
            RestConnectorError('http error'),
            requests.exceptions.ConnectionError('connection refused'),
        ):
            connector = MagicMock()
            connector.get.side_effect = error

            with (
                override_settings(DJANGO_SPIRE_METRIC_REMOTE_TARGETS=TARGETS),
                patch(
                    'django_spire.metric.metric.SpireMetricRestConnector', return_value=connector
                ),
            ):
                summary = RemoteMetric.check()

            assert summary.ok is False
            assert summary.missing == ['store/orders/created']
            assert any('sub-domains not checked' in error for error in summary.errors)
