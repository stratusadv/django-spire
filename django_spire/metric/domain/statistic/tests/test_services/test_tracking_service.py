from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from django.test import override_settings

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
        with override_settings(
            DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY=str(self.statistic.key),
            DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY=str(self.sub_domain.key),
        ):
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

        with override_settings(
            DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY=str(self.statistic.key),
            DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY=str(self.sub_domain.key),
        ):
            value = StatisticTrackingService.track_configured(reference='page_click')

            assert value is None
            assert not StatisticValue.objects.exists()

    def test_track_configured_is_noop_for_inactive_sub_domain(self) -> None:
        self.sub_domain.set_inactive()

        with override_settings(
            DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY=str(self.statistic.key),
            DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY=str(self.sub_domain.key),
        ):
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

    def test_track_trims_old_values_beyond_retention_cap(self) -> None:
        with override_settings(DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX=3):
            for _ in range(7):
                self.statistic.services.tracking.track(self.sub_domain, reference='click')

            assert StatisticValue.objects.count() == 3

    def test_track_keeps_values_within_retention_cap(self) -> None:
        with override_settings(DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX=10):
            for _ in range(5):
                self.statistic.services.tracking.track(self.sub_domain, reference='click')

            assert StatisticValue.objects.count() == 5

    def test_track_trims_only_values_for_tracked_key(self) -> None:
        with override_settings(DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX=2):
            for _ in range(5):
                self.statistic.services.tracking.track(self.sub_domain, reference='click')

            self.statistic.services.tracking.track(self.sub_domain, reference='other')

            assert StatisticValue.objects.filter(reference='click').count() == 2
            assert StatisticValue.objects.filter(reference='other').count() == 1
