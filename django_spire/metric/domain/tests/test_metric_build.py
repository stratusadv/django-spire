from __future__ import annotations

from decimal import Decimal

import pytest
from django.test import TransactionTestCase
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric import Metric
from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.statistic.models import Statistic, StatisticGroup, StatisticValue


class StoreMetric(Metric):
    domains = [
        Metric.Domain(
            'store',
            name='Store',
            description='Storefront sales and fulfillment metrics.',
            sub_domain_name='Channels',
            subdomains=[
                Metric.SubDomain('web', name='Web'),
                Metric.SubDomain('retail', name='Retail'),
            ],
            statistic_groups=[
                Metric.StatisticGroup(
                    'orders',
                    name='Orders',
                    statistics=[
                        Metric.Statistic('created', name='Orders created'),
                        Metric.Statistic('revenue', name='Order revenue', value_type='currency'),
                    ],
                )
            ],
        )
    ]


class MetricBuildTestCase(BaseTestCase):
    def test_build_creates_structure(self):
        summary = StoreMetric.build()

        assert summary.created == 6
        assert summary.errors == []

        domain = Domain.objects.for_key('store').get()
        assert domain.name == 'Store'
        assert domain.sub_domain_name == 'Channels'
        assert SubDomain.objects.for_key('store__web').exists()
        assert SubDomain.objects.for_key('store__retail').exists()
        assert StatisticGroup.objects.for_key('store__orders').exists()
        assert Statistic.objects.for_key('store__orders__created').exists()
        assert Statistic.objects.for_key('store__orders__revenue').get().value_type == 'currency'

    def test_build_is_idempotent(self):
        StoreMetric.build()
        summary = StoreMetric.build()

        assert summary.created == 0
        assert summary.updated == 0
        assert summary.unchanged == 6
        assert Domain.objects.count() == 1
        assert SubDomain.objects.count() == 2
        assert StatisticGroup.objects.count() == 1
        assert Statistic.objects.count() == 2

    def test_build_updates_drifted_values(self):
        StoreMetric.build()
        domain = Domain.objects.for_key('store').get()
        domain.name = 'Renamed'
        domain.save()

        summary = StoreMetric.build()

        assert summary.updated == 1
        assert summary.unchanged == 5
        assert Domain.objects.for_key('store').get().name == 'Store'

    def test_check_reports_missing_domain(self):
        summary = StoreMetric.check()

        assert summary.ok is False
        assert summary.missing == ['store']

    def test_check_reports_missing_statistic(self):
        StoreMetric.build()
        Statistic.objects.for_key('store__orders__revenue').get().set_deleted()

        summary = StoreMetric.check()

        assert summary.missing == ['store/orders/revenue']
        assert summary.ok is False

    def test_check_passes_after_build(self):
        StoreMetric.build()

        assert StoreMetric.check().ok is True

    def test_build_reports_deleted_domain_without_resurrecting(self):
        StoreMetric.build()
        Domain.objects.for_key('store').get().set_deleted()

        summary = StoreMetric.build()

        assert summary.errors
        assert 'deleted' in summary.errors[0]
        assert Domain.objects.for_key('store').get().is_deleted

    def test_build_reports_deleted_statistic_without_resurrecting(self):
        StoreMetric.build()
        Statistic.objects.for_key('store__orders__created').get().set_deleted()

        summary = StoreMetric.build()

        assert summary.errors
        assert 'store/orders/created' in summary.errors[0]
        assert Statistic.objects.for_key('store__orders__created').get().is_deleted

    def test_remote_registry_cannot_build(self):
        remote = type(
            'RemoteMetric',
            (Metric,),
            {
                'target': Metric.Target.REMOTE,
                'remote_target': 'central',
                'domains': [Metric.Domain('store', name='Store')],
            },
        )

        with pytest.raises(ValueError, match='targets a remote installation'):
            remote.build()


class MetricRecordTestCase(TransactionTestCase):
    def setUp(self) -> None:
        super().setUp()
        StoreMetric.build()

    def test_record_writes_value_with_default_reference(self):
        worker = StoreMetric.record('store', 'web', 'orders', 'created', value=3)
        worker.join()

        value = StatisticValue.objects.get(
            statistic__key='store__orders__created', sub_domain__key='store__web'
        )
        assert value.reference == 'store__orders__created'
        assert value.value == Decimal('3.0000')

    def test_record_accepts_explicit_reference(self):
        worker = StoreMetric.record(
            'store', 'retail', 'orders', 'created', reference='checkout', value=1
        )
        worker.join()

        value = StatisticValue.objects.get(
            statistic__key='store__orders__created', sub_domain__key='store__retail'
        )
        assert value.reference == 'checkout'

    def test_record_failure_is_swallowed(self):
        Statistic.objects.for_key('store__orders__created').get().set_deleted()

        worker = StoreMetric.record('store', 'web', 'orders', 'created', value=1)
        worker.join()

        assert not StatisticValue.objects.filter(statistic__key='store__orders__created').exists()

    def test_record_rejects_unknown_statistic(self):
        with pytest.raises(ValueError, match='No statistic declared for domain'):
            StoreMetric.record('store', 'web', 'orders', 'missing')

    def test_record_rejects_unknown_domain(self):
        with pytest.raises(ValueError, match='No statistic declared for domain'):
            StoreMetric.record('missing', 'web', 'orders', 'created')

    def test_record_rejects_unknown_sub_domain(self):
        with pytest.raises(ValueError, match='No sub-domain'):
            StoreMetric.record('store', 'missing', 'orders', 'created')
