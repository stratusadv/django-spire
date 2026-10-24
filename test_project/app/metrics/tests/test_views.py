from __future__ import annotations

from decimal import Decimal

from django.test import TransactionTestCase
from django.urls import reverse

from django_spire.auth.user.models import AuthUser
from django_spire.metric.domain.statistic.models import StatisticValue

from test_project.app.metrics.metrics import StoreMetric


class MetricRecordTestPageTestCase(TransactionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = AuthUser.objects.create_superuser(username='stratus')
        self.client.force_login(self.user)
        StoreMetric.build()

    def test_page_renders_with_actions(self):
        response = self.client.get(reverse('metrics:page:record_test'))

        assert response.status_code == 200
        assert b'Record 3 orders created (web)' in response.content
        assert b'No values recorded yet.' in response.content

    def test_click_records_value_with_collection_reference(self):
        self.client.post(reverse('metrics:page:record_click'), {'action': 'created_web'})

        value = StatisticValue.objects.get(statistic__key='store__orders__created', sub_domain__key='store__web')
        assert value.reference == 'order:created'
        assert value.value == Decimal('3.0000')

    def test_click_records_value_with_multi_segment_reference(self):
        self.client.post(reverse('metrics:page:record_click'), {'action': 'created_retail'})

        value = StatisticValue.objects.get(statistic__key='store__orders__created', sub_domain__key='store__retail')
        assert value.reference == 'order:created:checkout'
        assert value.value == Decimal('1.0000')

    def test_unknown_action_records_nothing(self):
        self.client.post(reverse('metrics:page:record_click'), {'action': 'bogus'})

        assert StatisticValue.objects.count() == 0
