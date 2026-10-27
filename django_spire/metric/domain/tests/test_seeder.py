from __future__ import annotations

from typing import TYPE_CHECKING

from django.test import TransactionTestCase

from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.seeding.constants import (
    DOMAIN_SEEDS,
    GROUP_SEEDS,
    STATISTIC_KEYS,
    SUB_DOMAIN_KEYS,
    SUBDOMAIN_SEEDS,
)
from django_spire.metric.domain.seeding.seeder import DomainSeeder, SubDomainSeeder
from django_spire.metric.domain.statistic.models import Statistic, StatisticGroup, StatisticValue
from django_spire.metric.domain.statistic.seeding.seeder import (
    StatisticGroupSeeder,
    StatisticSeeder,
    seed_statistic_values,
)
from django_spire.metric.visual.models import Visual, VisualCondition, VisualRegion
from django_spire.metric.visual.presentation.models import Presentation, Slide, SlideSection
from django_spire.metric.visual.presentation.seeding.constants import PRESENTATION_SEEDS
from django_spire.metric.visual.presentation.seeding.seeder import PresentationSeeder
from django_spire.metric.visual.seeding.constants import VISUAL_REGION_SEEDS, VISUAL_SEEDS
from django_spire.metric.visual.seeding.seeder import VisualRegionSeeder, VisualSeeder
from django_spire.metric.visual.signage.models import Signage, SignagePresentation
from django_spire.metric.visual.signage.seeding.constants import SIGNAGE_SEEDS
from django_spire.metric.visual.signage.seeding.seeder import SignageSeeder
from django_spire.contrib.seeding.field.seed.model_seed import BaseForeignKeyModelFieldSeed

if TYPE_CHECKING:
    from django.db.models import QuerySet


class DomainSeederTestCase(TransactionTestCase):
    def _seed_domains(self, count: int) -> QuerySet:
        seeder = DomainSeeder(count=count)
        seeder.cache_enabled = False
        return seeder.seed_database()

    def test_seeds_domains_with_realistic_constant_data(self):
        domains = list(self._seed_domains(count=len(DOMAIN_SEEDS)).order_by('pk'))

        assert len(domains) == len(DOMAIN_SEEDS)
        for domain, seed in zip(domains, DOMAIN_SEEDS, strict=True):
            assert domain.name == seed['name']
            assert domain.description == seed['description']
            assert domain.sub_domain_name == seed['sub_domain_name']

        assert all(domain.is_active for domain in domains)
        assert all(not domain.is_deleted for domain in domains)

    def test_domain_fields_are_populated_without_llm_or_lorem(self):
        domain = next(iter(self._seed_domains(count=1)))

        assert domain.description
        assert domain.sub_domain_name
        assert '' not in (domain.name, domain.description, domain.sub_domain_name)

    def test_seeding_more_domains_than_constant_data_wraps(self):
        domains = list(self._seed_domains(count=len(DOMAIN_SEEDS) * 2).order_by('pk'))
        names = {seed['name'] for seed in DOMAIN_SEEDS}

        assert len(domains) == len(DOMAIN_SEEDS) * 2
        assert all(domain.name in names for domain in domains)

        keys = [domain.key for domain in domains]
        assert len(set(keys)) == len(domains)
        assert all(key for key in keys)

    def test_seeding_skips_keys_of_existing_domains(self):
        Domain.objects.create(name='Sales', key='sales')
        domains = list(self._seed_domains(count=len(DOMAIN_SEEDS)).order_by('pk'))

        sales = next(domain for domain in domains if domain.name == 'Sales')

        assert sales.key == 'sales-2'
        assert len({domain.key for domain in domains} | {'sales'}) == len(domains) + 1


class SubDomainSeederTestCase(TransactionTestCase):
    def setUp(self) -> None:
        BaseForeignKeyModelFieldSeed._model_foreign_keys.clear()

    def _seed_domains_and_subdomains(
        self, domain_count: int, subdomain_count: int
    ) -> tuple[QuerySet, QuerySet]:
        domain_seeder = DomainSeeder(count=domain_count)
        domain_seeder.cache_enabled = False
        domains = domain_seeder.seed_database()

        subdomain_seeder = SubDomainSeeder(count=subdomain_count)
        subdomain_seeder.cache_enabled = False
        subdomains = subdomain_seeder.seed_database().order_by('pk')

        return domains, subdomains

    def test_seeds_sub_domains_with_realistic_constant_data(self):
        self._seed_domains_and_subdomains(
            domain_count=len(DOMAIN_SEEDS), subdomain_count=len(SUBDOMAIN_SEEDS)
        )
        subdomains = SubDomain.objects.order_by('pk')

        assert subdomains.count() == len(SUBDOMAIN_SEEDS)
        for subdomain, seed in zip(subdomains, SUBDOMAIN_SEEDS, strict=True):
            assert subdomain.name == seed['name']
            assert subdomain.description == seed['description']
            assert subdomain.domain.name == seed['domain']

        assert all(subdomain.is_active for subdomain in subdomains)
        assert all(not subdomain.is_deleted for subdomain in subdomains)

    def test_sub_domains_distribute_across_all_domains(self):
        domains, subdomains = self._seed_domains_and_subdomains(domain_count=3, subdomain_count=9)

        domain_ids = set(domains.values_list('id', flat=True))
        assert set(subdomains.values_list('domain_id', flat=True)) == domain_ids

    def test_sub_domains_only_reference_active_domains(self):
        domain_seeder = DomainSeeder(count=2)
        domain_seeder.cache_enabled = False
        domains = domain_seeder.seed_database()
        domains[0].set_deleted()

        subdomain_seeder = SubDomainSeeder(count=5)
        subdomain_seeder.cache_enabled = False
        subdomains = subdomain_seeder.seed_database()

        active_domain_ids = set(Domain.objects.active().values_list('id', flat=True))
        assert set(subdomains.values_list('domain_id', flat=True)) == active_domain_ids

    def test_seeding_more_sub_domains_than_keys_wraps_with_unique_keys(self):
        self._seed_domains_and_subdomains(
            domain_count=len(DOMAIN_SEEDS), subdomain_count=len(SUB_DOMAIN_KEYS) * 2
        )
        subdomains = SubDomain.objects.order_by('pk')

        assert subdomains.count() == len(SUB_DOMAIN_KEYS) * 2
        keys = list(subdomains.values_list('key', flat=True))
        assert len(set(keys)) == len(keys)

    def test_reseeding_sub_domains_skips_existing_keys(self):
        domain_seeder = DomainSeeder(count=len(DOMAIN_SEEDS))
        domain_seeder.cache_enabled = False
        domain_seeder.seed_database()

        subdomain_seeder = SubDomainSeeder(count=len(SUBDOMAIN_SEEDS))
        subdomain_seeder.cache_enabled = False
        subdomain_seeder.seed_database()
        subdomain_seeder.reseed_database()

        keys = list(SubDomain.objects.values_list('key', flat=True))

        assert len(keys) == len(SUBDOMAIN_SEEDS) * 2
        assert len(set(keys)) == len(keys)


class StatisticGroupSeederTestCase(TransactionTestCase):
    def setUp(self) -> None:
        BaseForeignKeyModelFieldSeed._model_foreign_keys.clear()

    def _seed_groups(self, count: int) -> QuerySet:
        seeder = StatisticGroupSeeder(count=count)
        seeder.cache_enabled = False
        return seeder.seed_database()

    def _seed_domains(self) -> QuerySet:
        domain_seeder = DomainSeeder(count=len(DOMAIN_SEEDS))
        domain_seeder.cache_enabled = False
        return domain_seeder.seed_database()

    def test_seeded_group_keys_are_unique_across_wrapped_names(self):
        self._seed_domains()
        groups = list(self._seed_groups(count=len(GROUP_SEEDS) * 2).order_by('pk'))

        assert len(groups) == len(GROUP_SEEDS) * 2
        keys = [group.key for group in groups]
        assert len(set(keys)) == len(groups)
        assert all(key for key in keys)

    def test_seeding_skips_keys_of_existing_groups(self):
        domains = self._seed_domains()
        domain = domains.order_by('pk').first()
        StatisticGroup.objects.create(domain=domain, name='Pipeline Performance')

        groups = list(self._seed_groups(count=len(GROUP_SEEDS)).order_by('pk'))
        seeded_group = next(group for group in groups if group.name == 'Pipeline Performance')

        assert seeded_group.key == 'sales-pipeline-performance-2'
        assert len({group.key for group in groups}) == len(groups)


class StatisticSeederTestCase(TransactionTestCase):
    def setUp(self) -> None:
        BaseForeignKeyModelFieldSeed._model_foreign_keys.clear()

    def _seed_groups(self) -> QuerySet:
        domain_seeder = DomainSeeder(count=len(DOMAIN_SEEDS))
        domain_seeder.cache_enabled = False
        domain_seeder.seed_database()

        group_seeder = StatisticGroupSeeder(count=5)
        group_seeder.cache_enabled = False
        return group_seeder.seed_database()

    def _seed_statistics(self, count: int) -> QuerySet:
        seeder = StatisticSeeder(count=count)
        seeder.cache_enabled = False
        return seeder.seed_database()

    def test_seeding_more_statistics_than_keys_wraps_with_unique_keys(self):
        self._seed_groups()
        statistics = list(self._seed_statistics(count=len(STATISTIC_KEYS) * 2).order_by('pk'))

        assert len(statistics) == len(STATISTIC_KEYS) * 2
        keys = [statistic.key for statistic in statistics]
        assert len(set(keys)) == len(statistics)
        assert all(key for key in keys)

    def test_reseeding_statistics_skips_existing_keys(self):
        self._seed_groups()
        seeder = StatisticSeeder(count=len(STATISTIC_KEYS))
        seeder.cache_enabled = False
        seeder.seed_database()
        seeder.reseed_database()

        keys = list(Statistic.objects.values_list('key', flat=True))

        assert len(keys) == len(STATISTIC_KEYS) * 2
        assert len(set(keys)) == len(keys)


class MetricSeedingSmokeTestCase(TransactionTestCase):
    def setUp(self) -> None:
        BaseForeignKeyModelFieldSeed._model_foreign_keys.clear()

    def _run_full_seed(self) -> None:
        DomainSeeder(count=len(DOMAIN_SEEDS), verbose=False).seed_database()
        SubDomainSeeder(count=len(SUBDOMAIN_SEEDS), verbose=False).seed_database()
        StatisticGroupSeeder(count=5, verbose=False).seed_database()
        StatisticSeeder(count=12, verbose=False).seed_database()
        seed_statistic_values(count=1000)
        VisualSeeder(count=len(VISUAL_SEEDS), verbose=False).seed_database()
        VisualRegionSeeder(count=len(VISUAL_REGION_SEEDS), verbose=False).seed_database()
        PresentationSeeder(count=len(PRESENTATION_SEEDS), verbose=False).seed_database()
        SignageSeeder(count=len(SIGNAGE_SEEDS), verbose=False).seed_database()

    def test_full_seed_creates_expected_rows(self) -> None:
        self._run_full_seed()

        assert Domain.objects.count() == len(DOMAIN_SEEDS)
        assert SubDomain.objects.count() == len(SUBDOMAIN_SEEDS)
        assert StatisticGroup.objects.count() == 5
        assert Statistic.objects.count() == 12
        assert StatisticValue.objects.count() > 0
        assert Visual.objects.count() == len(VISUAL_SEEDS)
        assert VisualCondition.objects.count() > 0
        assert VisualRegion.objects.count() == len(VISUAL_REGION_SEEDS)
        assert Presentation.objects.count() == len(PRESENTATION_SEEDS)
        assert Slide.objects.count() > 0
        assert SlideSection.objects.count() > 0
        assert Signage.objects.count() == len(SIGNAGE_SEEDS)
        assert SignagePresentation.objects.count() > 0
