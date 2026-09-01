from __future__ import annotations

from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.models import StatisticValue
from django_spire.metric.domain.statistic.queue import StatisticTrackingQueue
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
)


class StatisticTrackingQueueTestCase(BaseTestCase):
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

    def test_enqueue_accepts_references(self) -> None:
        tracking_queue = StatisticTrackingQueue(start_worker=False)

        assert tracking_queue.enqueue('click') is True
        assert tracking_queue.enqueue('other') is True

    def test_enqueue_drops_when_queue_full(self) -> None:
        tracking_queue = StatisticTrackingQueue(maxsize=1, start_worker=False)

        assert tracking_queue.enqueue('click') is True
        assert tracking_queue.enqueue('other') is False

    def test_flush_writes_batched_values(self) -> None:
        tracking_queue = StatisticTrackingQueue(start_worker=False)
        tracking_queue.enqueue('click')
        tracking_queue.enqueue('click')
        tracking_queue.enqueue('other')

        with self._tracking_settings():
            tracking_queue.flush()

        values = StatisticValue.objects.order_by('pk')
        assert values.count() == 3
        assert {value.reference for value in values} == {'click', 'other'}
        assert all(value.statistic == self.statistic for value in values)
        assert all(value.sub_domain == self.sub_domain for value in values)

    def test_flush_is_noop_when_empty(self) -> None:
        tracking_queue = StatisticTrackingQueue(start_worker=False)

        with self._tracking_settings():
            tracking_queue.flush()

        assert not StatisticValue.objects.exists()
