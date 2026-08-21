from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.models import StatisticValue
from django_spire.metric.domain.statistic.seeding.seeder import seed_statistic_values
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
)


class SeedStatisticValuesTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain(name='value_domain')
        self.sub_domain = create_test_subdomain(domain=self.domain, name='value_subdomain')
        self.other_domain = create_test_domain(name='other_domain')
        self.other_group = create_test_statistic_group(domain=self.other_domain, name='other_group')
        self.other_statistic = create_test_statistic(group=self.other_group, name='other_statistic')
        self.group = create_test_statistic_group(domain=self.domain, name='value_group')
        self.statistic = create_test_statistic(group=self.group, name='value_statistic')

    def test_seeded_values_only_reference_their_statistic_domain(self):
        seed_statistic_values(count=50)

        assert StatisticValue.objects.count() == 50

        for value in StatisticValue.objects.select_related(
            'sub_domain__domain', 'statistic__group__domain'
        ):
            assert value.sub_domain.domain_id == value.statistic.group.domain_id

    def test_statistic_without_domain_sub_domains_gets_no_values(self):
        seed_statistic_values(count=50)

        assert StatisticValue.objects.filter(statistic=self.other_statistic).count() == 0
        assert StatisticValue.objects.filter(statistic=self.statistic).count() == 50
