from __future__ import annotations

from datetime import timedelta

from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.models import StatisticValue
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
)


class PruneMetricStatisticValuesCommandTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def test_command_prunes_retention_and_trims_caps(self) -> None:
        self.statistic.services.processor.add_value(
            reference='old',
            sub_domain=self.sub_domain,
            value=1,
            value_timestamp=timezone.now() - timedelta(days=30),
        )
        for _ in range(5):
            self.statistic.services.tracking.track(self.sub_domain, reference='click')

        with override_settings(DJANGO_SPIRE_METRIC_RETENTION_DAYS=7):
            call_command('prune_metric_statistic_values')

        assert StatisticValue.objects.filter(reference='old').count() == 0
        assert StatisticValue.objects.filter(reference='click').count() == 5
