from __future__ import annotations

from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.models import SubDomain
from django_spire.metric.domain.seeding.constants import (
    INTERNAL_TRACKING_STATISTIC_KEY,
    INTERNAL_TRACKING_SUB_DOMAIN_KEY,
)
from django_spire.metric.domain.statistic.models import Statistic
from django_spire.metric.domain.statistic.services.tracking_service import StatisticTrackingService
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic_group,
)


class SeededStatisticTrackingServiceTestCase(BaseTestCase):
    def test_tracks_page_click_against_seeded_statistic(self) -> None:
        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = Statistic.objects.create(
            group=group, name='Clicks', key=INTERNAL_TRACKING_STATISTIC_KEY
        )
        SubDomain.objects.create(
            domain=domain, name='Website Traffic', key=INTERNAL_TRACKING_SUB_DOMAIN_KEY
        )

        with override_settings(
            DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY=INTERNAL_TRACKING_STATISTIC_KEY,
            DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY=INTERNAL_TRACKING_SUB_DOMAIN_KEY,
        ):
            value = StatisticTrackingService.track_configured(reference='page_click')

        assert value is not None
        assert value.statistic == statistic
        assert value.statistic.key == INTERNAL_TRACKING_STATISTIC_KEY
        assert value.sub_domain.key == INTERNAL_TRACKING_SUB_DOMAIN_KEY
        assert value.reference == 'page_click'
