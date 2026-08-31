from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from django.test import override_settings
from django.utils import timezone

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.models import StatisticValue
from django_spire.metric.domain.statistic.services.tracking_service import StatisticTrackingService
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
)


class StatisticTrackingServiceTestCase(BaseTestCase):
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

    def test_track_creates_value(self) -> None:
        value = self.statistic.services.tracking.track(self.sub_domain, reference='page_click')

        assert value is not None
        assert value.statistic == self.statistic
        assert value.sub_domain == self.sub_domain
        assert value.reference == 'page_click'
        assert value.value == Decimal(1)

    def test_track_rejects_sub_domain_outside_domain(self) -> None:
        foreign_domain = create_test_domain(name='foreign_domain')
        foreign_sub_domain = create_test_subdomain(domain=foreign_domain)

        value = self.statistic.services.tracking.track(foreign_sub_domain, reference='page_click')

        assert value is None
        assert not StatisticValue.objects.exists()

    def test_track_configured_reads_keys_from_settings(self) -> None:
        with self._tracking_settings():
            value = StatisticTrackingService.track_configured(reference='click')

            assert value is not None
            assert value.statistic == self.statistic
            assert value.reference == 'click'

    def test_track_configured_is_noop_without_settings(self) -> None:
        with override_settings(
            DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY='',
            DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY='',
        ):
            value = StatisticTrackingService.track_configured(reference='page_click')

            assert value is None
            assert not StatisticValue.objects.exists()

    def test_track_configured_is_noop_for_missing_target(self) -> None:
        with override_settings(
            DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY=str(uuid4()),
            DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY=str(uuid4()),
        ):
            value = StatisticTrackingService.track_configured(reference='page_click')

            assert value is None
            assert not StatisticValue.objects.exists()

    def test_track_configured_is_noop_for_inactive_statistic(self) -> None:
        self.statistic.set_inactive()

        with self._tracking_settings():
            value = StatisticTrackingService.track_configured(reference='page_click')

            assert value is None
            assert not StatisticValue.objects.exists()

    def test_track_configured_is_noop_for_inactive_sub_domain(self) -> None:
        self.sub_domain.set_inactive()

        with self._tracking_settings():
            value = StatisticTrackingService.track_configured(reference='page_click')

            assert value is None
            assert not StatisticValue.objects.exists()

    def test_track_configured_is_noop_for_invalid_key(self) -> None:
        with override_settings(
            DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY='not-a-uuid',
            DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY=str(self.sub_domain.key),
        ):
            value = StatisticTrackingService.track_configured(reference='page_click')

            assert value is None
            assert not StatisticValue.objects.exists()

    def test_track_many_batches_references(self) -> None:
        with self._tracking_settings():
            StatisticTrackingService.track_many(['click', 'click', 'other'])

        values = StatisticValue.objects.order_by('pk')
        assert values.count() == 3
        assert {value.reference for value in values} == {'click', 'other'}
        assert all(value.statistic == self.statistic for value in values)
        assert all(value.sub_domain == self.sub_domain for value in values)

    def test_track_many_is_noop_without_settings(self) -> None:
        with override_settings(
            DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY='',
            DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY='',
        ):
            StatisticTrackingService.track_many(['click', 'other'])

        assert not StatisticValue.objects.exists()

    def test_track_many_rejects_sub_domain_outside_domain(self) -> None:
        foreign_domain = create_test_domain(name='foreign_domain')
        foreign_sub_domain = create_test_subdomain(domain=foreign_domain)

        with override_settings(
            DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY=str(self.statistic.key),
            DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY=str(foreign_sub_domain.key),
        ):
            StatisticTrackingService.track_many(['click', 'other'])

        assert not StatisticValue.objects.exists()

    def test_trim_removes_oldest_values_beyond_cap(self) -> None:
        with override_settings(DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX=3):
            for _ in range(7):
                self.statistic.services.tracking.track(self.sub_domain, reference='click')

            deleted = self.statistic.services.tracking.trim(self.sub_domain, reference='click')

            assert deleted == 4
            assert StatisticValue.objects.count() == 3

    def test_trim_removes_oldest_values_first(self) -> None:
        for _ in range(5):
            self.statistic.services.tracking.track(self.sub_domain, reference='click')

        latest = StatisticValue.objects.latest('pk')

        self.statistic.services.tracking.trim(self.sub_domain, reference='click', max_values=2)

        remaining = list(StatisticValue.objects.order_by('timestamp'))
        assert len(remaining) == 2
        assert remaining[-1].pk == latest.pk

    def test_trim_leaves_values_within_cap_untouched(self) -> None:
        for _ in range(5):
            self.statistic.services.tracking.track(self.sub_domain, reference='click')

        deleted = self.statistic.services.tracking.trim(
            self.sub_domain, reference='click', max_values=10
        )

        assert deleted == 0
        assert StatisticValue.objects.count() == 5

    def test_trim_only_affects_tracked_key(self) -> None:
        for _ in range(5):
            self.statistic.services.tracking.track(self.sub_domain, reference='click')
        self.statistic.services.tracking.track(self.sub_domain, reference='other')

        self.statistic.services.tracking.trim(self.sub_domain, reference='click', max_values=2)

        assert StatisticValue.objects.filter(reference='click').count() == 2
        assert StatisticValue.objects.filter(reference='other').count() == 1

    def test_trim_all_trims_every_group(self) -> None:
        with override_settings(DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX=2):
            second_sub_domain = create_test_subdomain(domain=self.domain, name='second')

            for _ in range(5):
                self.statistic.services.tracking.track(self.sub_domain, reference='click')
            for _ in range(4):
                self.statistic.services.tracking.track(second_sub_domain, reference='click')
            for _ in range(3):
                self.statistic.services.tracking.track(second_sub_domain, reference='other')

            deleted = StatisticTrackingService.trim_all()

            assert deleted == (5 - 2) + (4 - 2) + (3 - 2)
            assert StatisticValue.objects.filter(sub_domain=self.sub_domain).count() == 2
            assert (
                StatisticValue.objects.filter(
                    sub_domain=second_sub_domain, reference='click'
                ).count()
                == 2
            )
            assert (
                StatisticValue.objects.filter(
                    sub_domain=second_sub_domain, reference='other'
                ).count()
                == 2
            )

    def test_prune_retention_removes_rows_older_than_cutoff(self) -> None:
        self.statistic.services.processor.add_value(
            reference='old',
            sub_domain=self.sub_domain,
            value=1,
            value_timestamp=timezone.now() - timedelta(days=30),
        )
        self.statistic.services.processor.add_value(
            reference='old', sub_domain=self.sub_domain, value=1
        )

        deleted = StatisticTrackingService.prune_retention(retention_days=7)

        assert deleted == 1
        assert StatisticValue.objects.count() == 1
        assert StatisticValue.objects.get().reference == 'old'
        assert StatisticValue.objects.get().timestamp >= timezone.now() - timedelta(days=7)

    def test_prune_retention_disabled_when_retention_days_zero(self) -> None:
        self.statistic.services.processor.add_value(
            reference='old',
            sub_domain=self.sub_domain,
            value=1,
            value_timestamp=timezone.now() - timedelta(days=30),
        )

        deleted = StatisticTrackingService.prune_retention(retention_days=0)

        assert deleted == 0
        assert StatisticValue.objects.count() == 1
