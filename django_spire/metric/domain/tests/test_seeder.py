from __future__ import annotations

from typing import TYPE_CHECKING

from django.test import TransactionTestCase

from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.seeding.constants import DOMAIN_SEEDS, SUBDOMAIN_SEEDS
from django_spire.metric.domain.seeding.seeder import DomainSeeder, SubDomainSeeder
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
            assert domain.sub_domain_description == seed['sub_domain_description']

        assert all(domain.is_active for domain in domains)
        assert all(not domain.is_deleted for domain in domains)

    def test_domain_fields_are_populated_without_llm_or_lorem(self):
        domain = next(iter(self._seed_domains(count=1)))

        assert domain.description
        assert domain.sub_domain_description
        assert '' not in (domain.name, domain.description, domain.sub_domain_description)

    def test_seeding_more_domains_than_constant_data_wraps(self):
        domains = list(self._seed_domains(count=len(DOMAIN_SEEDS) * 2).order_by('pk'))
        names = {seed['name'] for seed in DOMAIN_SEEDS}

        assert len(domains) == len(DOMAIN_SEEDS) * 2
        assert all(domain.name in names for domain in domains)


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
        self._seed_domains_and_subdomains(domain_count=1, subdomain_count=len(SUBDOMAIN_SEEDS))
        subdomains = SubDomain.objects.order_by('pk')

        assert subdomains.count() == len(SUBDOMAIN_SEEDS)
        for subdomain, seed in zip(subdomains, SUBDOMAIN_SEEDS, strict=True):
            assert subdomain.name == seed['name']
            assert subdomain.description == seed['description']

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
