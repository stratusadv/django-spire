from __future__ import annotations

from django_spire.contrib.seeding import Seeder
from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.seeding.constants import (
    DOMAIN_SEEDS,
    SUB_DOMAIN_KEYS,
    SUBDOMAIN_SEEDS,
)


class DomainSeeder(Seeder):
    cache_enabled = False
    model_class = Domain

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'name': Seeder.ordered.choice([seed['name'] for seed in DOMAIN_SEEDS], wrap=True),
        'description': Seeder.ordered.choice(
            [seed['description'] for seed in DOMAIN_SEEDS], wrap=True
        ),
        'sub_domain_name': Seeder.ordered.choice(
            [seed['sub_domain_name'] for seed in DOMAIN_SEEDS], wrap=True
        ),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }


class SubDomainSeeder(Seeder):
    cache_enabled = False
    model_class = SubDomain

    fields_seeds = {
        'id': Seeder.exclude(),
        'key': Seeder.ordered.choice(SUB_DOMAIN_KEYS, wrap=True),
        'domain_id': Seeder.model.ordered_queryset_foreign_key(Domain.objects.active(), wrap=True),
        'name': Seeder.ordered.choice([seed['name'] for seed in SUBDOMAIN_SEEDS], wrap=True),
        'description': Seeder.ordered.choice(
            [seed['description'] for seed in SUBDOMAIN_SEEDS], wrap=True
        ),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def __post_seed_database__(self) -> None:
        domains = {domain.name: domain for domain in Domain.objects.active()}
        updates = []

        for index, subdomain in enumerate(self.queryset.order_by('pk')):
            seed = SUBDOMAIN_SEEDS[index % len(SUBDOMAIN_SEEDS)]
            domain = domains.get(seed['domain'])

            if domain is None or domain.pk == subdomain.domain_id:
                continue

            subdomain.domain = domain
            updates.append(subdomain)

        SubDomain.objects.bulk_update(updates, ['domain'])
