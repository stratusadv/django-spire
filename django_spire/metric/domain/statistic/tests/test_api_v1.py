from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime, timedelta

from django.urls import reverse
from django.utils import timezone

from django_spire.api.choices import ApiPermissionChoices
from django_spire.constants import BASE_URL_NAME
from django_spire.api.models import ApiAccess
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.tests.factories import create_test_domain
from django_spire.metric.domain.tests.factories import create_test_subdomain
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_statistic,
    create_test_statistic_group,
)
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_subdomain as create_test_statistic_subdomain,
)


class BaseStatisticApiTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.raw_api_key = 'test_statistic_api_key'
        self.api_access = ApiAccess.objects.create(
            name='Statistic API', permission=ApiPermissionChoices.DELETE
        )
        self.api_access.set_key_and_save(self.raw_api_key)

        self.domain = create_test_domain(name='test_domain_id', description='description')
        self.sub_domain = create_test_statistic_subdomain(
            domain=self.domain, name='statistic_sub_domain'
        )
        self.second_sub_domain = create_test_statistic_subdomain(
            domain=self.domain, name='second_sub_domain'
        )
        foreign_domain = create_test_domain(name='foreign_domain', description='foreign')
        self.foreign_sub_domain = create_test_subdomain(domain=foreign_domain, name='foreign')
        self.group = create_test_statistic_group(domain=self.domain, name='api_group')
        self.statistic = create_test_statistic(group=self.group, name='api_statistic')

    def api_extra(self) -> dict:
        return {'HTTP_X_API_KEY': self.raw_api_key}

    def record_url(self, statistic_key: str | uuid.UUID | None = None) -> str:
        if statistic_key is None:
            statistic_key = self.statistic.key

        return reverse(
            f'{BASE_URL_NAME}:api_v1:record_value', kwargs={'statistic_key': str(statistic_key)}
        )

    def total_url(self) -> str:
        return reverse(
            f'{BASE_URL_NAME}:api_v1:total_for_interval',
            kwargs={'statistic_key': str(self.statistic.key)},
        )

    def values_url(self) -> str:
        return reverse(
            f'{BASE_URL_NAME}:api_v1:values_for_interval',
            kwargs={'statistic_key': str(self.statistic.key)},
        )

    def record_payload(self, **kwargs) -> dict:
        data = {'reference': 'client_site', 'sub_domain_key': str(self.sub_domain.key), 'value': 1}
        data.update(kwargs)
        return data

    def post_record(self, url: str, payload: dict | None = None, extra: dict | None = None):
        if payload is None:
            payload = self.record_payload()

        return self.client.post(
            url, data=json.dumps(payload), content_type='application/json', **(extra or {})
        )


class RecordValueApiTestCase(BaseStatisticApiTestCase):
    def test_record_value_requires_api_key(self):
        response = self.post_record(self.record_url())

        assert response.status_code == 401

    def test_record_value_creates_entry(self):
        response = self.post_record(self.record_url(), extra=self.api_extra())

        assert response.status_code == 200
        body = response.json()
        assert body['statistic_key'] == str(self.statistic.key)
        assert body['sub_domain_key'] == str(self.sub_domain.key)
        assert body['reference'] == 'client_site'
        assert float(body['value']) == 1.0
        timestamp = datetime.fromisoformat(body['timestamp'])
        assert abs((timestamp - datetime.now(UTC)).total_seconds()) < 5

    def test_record_value_total_matches_recorded_value(self):
        self.post_record(self.record_url(), extra=self.api_extra())
        self.post_record(self.record_url(), self.record_payload(value=2), extra=self.api_extra())

        assert float(self.statistic.values.total()) == 3.0

    def test_record_value_without_sub_domain_key_is_invalid(self):
        payload = self.record_payload()
        del payload['sub_domain_key']

        response = self.post_record(self.record_url(), payload, extra=self.api_extra())

        assert response.status_code == 422
        self.assertQuerySetEqual(self.statistic.values.all(), [], transform=str)

    def test_record_value_with_malformed_sub_domain_key_is_invalid(self):
        response = self.post_record(
            self.record_url(),
            self.record_payload(sub_domain_key='not-a-uuid'),
            extra=self.api_extra(),
        )

        assert response.status_code == 422

    def test_record_value_rejects_foreign_sub_domain(self):
        response = self.post_record(
            self.record_url(),
            self.record_payload(sub_domain_key=str(self.foreign_sub_domain.key)),
            extra=self.api_extra(),
        )

        assert response.status_code == 404
        self.assertQuerySetEqual(self.statistic.values.all(), [], transform=str)

    def test_record_unknown_statistic_key_returns_404(self):
        response = self.post_record(self.record_url(uuid.uuid4()), extra=self.api_extra())

        assert response.status_code == 404

    def test_record_malformed_statistic_key_returns_404(self):
        response = self.post_record(self.record_url('not-a-uuid'), extra=self.api_extra())

        assert response.status_code == 404

    def test_record_value_is_raw_append(self):
        self.post_record(self.record_url(), extra=self.api_extra())
        self.post_record(self.record_url(), extra=self.api_extra())
        self.post_record(self.record_url(), self.record_payload(value=2), extra=self.api_extra())

        assert self.statistic.values.count() == 3
        total = float(sum(v.value for v in self.statistic.values.all()))
        assert total >= 4.0

    def test_record_value_rejects_reference_over_max_length(self):
        response = self.post_record(
            self.record_url(), self.record_payload(reference='x' * 256), extra=self.api_extra()
        )

        assert response.status_code == 422
        self.assertQuerySetEqual(self.statistic.values.all(), [], transform=str)

    def test_record_value_accepts_reference_at_max_length(self):
        response = self.post_record(
            self.record_url(), self.record_payload(reference='x' * 255), extra=self.api_extra()
        )

        assert response.status_code == 200
        assert response.json()['reference'] == 'x' * 255

    def test_record_soft_deleted_statistic_returns_404(self):
        self.statistic.set_deleted()

        response = self.post_record(self.record_url(), extra=self.api_extra())

        assert response.status_code == 404
        self.assertQuerySetEqual(self.statistic.values.all(), [], transform=str)

    def test_record_inactive_statistic_returns_404(self):
        self.statistic.set_inactive()

        response = self.post_record(self.record_url(), extra=self.api_extra())

        assert response.status_code == 404
        self.assertQuerySetEqual(self.statistic.values.all(), [], transform=str)

    def test_record_soft_deleted_sub_domain_returns_404(self):
        self.sub_domain.set_deleted()

        response = self.post_record(self.record_url(), extra=self.api_extra())

        assert response.status_code == 404
        self.assertQuerySetEqual(self.statistic.values.all(), [], transform=str)

    def test_record_inactive_sub_domain_returns_404(self):
        self.sub_domain.set_inactive()

        response = self.post_record(self.record_url(), extra=self.api_extra())

        assert response.status_code == 404
        self.assertQuerySetEqual(self.statistic.values.all(), [], transform=str)


class TotalForIntervalApiTestCase(BaseStatisticApiTestCase):
    def test_total_requires_api_key(self):
        response = self.client.get(self.total_url())

        assert response.status_code == 401

    def test_total_returns_interval(self):
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.sub_domain, value=5
        )

        response = self.client.get(self.total_url(), **self.api_extra())

        assert response.status_code == 200
        body = response.json()
        assert body['date'] is None
        assert float(body['total']) == 5.0

    def test_total_for_single_date(self):
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.sub_domain, value=5
        )
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.sub_domain, value=3
        )

        value_date = timezone.localdate()
        response = self.client.get(
            self.total_url() + f'?value_date={value_date}', **self.api_extra()
        )

        assert response.status_code == 200
        body = response.json()
        assert body['date'] == value_date.isoformat()
        assert body['start_date'] == value_date.isoformat()
        assert body['end_date'] == value_date.isoformat()
        assert float(body['total']) == 8.0

    def test_total_filters_by_sub_domain_key(self):
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.sub_domain, value=5
        )
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.second_sub_domain, value=3
        )

        response = self.client.get(
            self.total_url() + f'?sub_domain_key={self.sub_domain.key}', **self.api_extra()
        )

        assert response.status_code == 200
        assert float(response.json()['total']) == 5.0

    def test_total_is_zero_on_soft_deleted_statistic(self):
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.sub_domain, value=5
        )
        self.statistic.set_deleted()

        response = self.client.get(self.total_url(), **self.api_extra())

        assert response.status_code == 200
        assert float(response.json()['total']) == 0.0


class ValuesForIntervalApiTestCase(BaseStatisticApiTestCase):
    def test_values_requires_api_key(self):
        response = self.client.get(self.values_url())

        assert response.status_code == 401

    def test_values_for_interval_returns_raw_entries(self):
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.sub_domain, value=1
        )
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.sub_domain, value=2
        )

        response = self.client.get(self.values_url(), **self.api_extra())

        assert response.status_code == 200
        body = response.json()
        assert len(body) == 2
        for row in body:
            assert row['statistic_key'] == str(self.statistic.key)
            assert row['sub_domain_key'] == str(self.sub_domain.key)
            assert row['reference'] == 'client_site'

        assert float(sum(float(row['value']) for row in body)) == 3.0

    def test_values_filter_by_sub_domain_key(self):
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.sub_domain, value=1
        )
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.second_sub_domain, value=2
        )

        response = self.client.get(
            self.values_url() + f'?sub_domain_key={self.sub_domain.key}', **self.api_extra()
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]['sub_domain_key'] == str(self.sub_domain.key)
        assert float(body[0]['value']) == 1.0

    def test_values_filter_by_foreign_sub_domain_key_returns_404(self):
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.sub_domain, value=1
        )

        response = self.client.get(
            self.values_url() + f'?sub_domain_key={self.foreign_sub_domain.key}', **self.api_extra()
        )

        assert response.status_code == 404

    def test_values_respects_limit_and_offset(self):
        for index in range(5):
            self.statistic.services.processor.add_value(
                reference='client_site',
                sub_domain=self.sub_domain,
                value=index,
                value_timestamp=timezone.now() + timedelta(seconds=index),
            )

        response = self.client.get(self.values_url() + '?limit=2&offset=1', **self.api_extra())

        assert response.status_code == 200
        body = response.json()
        assert len(body) == 2
        assert [float(row['value']) for row in body] == [1.0, 2.0]

    def test_values_rejects_limit_over_max(self):
        response = self.client.get(self.values_url() + '?limit=5001', **self.api_extra())

        assert response.status_code == 422


class IntervalSummaryApiTestCase(BaseStatisticApiTestCase):
    def summary_url(self) -> str:
        return reverse(
            f'{BASE_URL_NAME}:api_v1:interval_summary',
            kwargs={'statistic_key': str(self.statistic.key)},
        )

    def get_summary(self, sub_domain_key: str | None = None):
        value_date = timezone.localdate().isoformat()
        url = f'{self.summary_url()}?start_date={value_date}&end_date={value_date}'
        if sub_domain_key is not None:
            url += f'&sub_domain_key={sub_domain_key}'

        return self.client.get(url, **self.api_extra())

    def test_summary_requires_api_key(self):
        value_date = timezone.localdate().isoformat()
        response = self.client.get(
            f'{self.summary_url()}?start_date={value_date}&end_date={value_date}'
        )

        assert response.status_code == 401

    def test_summary_buckets_values_per_interval(self):
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.sub_domain, value=1
        )
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.second_sub_domain, value=2
        )

        body = self.get_summary().json()

        assert sum(float(total) for total in body['totals'].values()) == 3.0

    def test_summary_filters_by_sub_domain_key(self):
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.sub_domain, value=5
        )
        self.statistic.services.processor.add_value(
            reference='client_site', sub_domain=self.second_sub_domain, value=3
        )

        body = self.get_summary(sub_domain_key=str(self.sub_domain.key)).json()

        assert sum(float(total) for total in body['totals'].values()) == 5.0

    def test_summary_foreign_sub_domain_key_returns_404(self):
        response = self.get_summary(sub_domain_key=str(self.foreign_sub_domain.key))

        assert response.status_code == 404
