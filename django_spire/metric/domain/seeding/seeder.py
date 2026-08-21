from django_spire.contrib.seeding import Seeder
from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.seeding.constants import (
    DOMAIN_SEEDS,
    SUB_DOMAIN_KEYS,
    SUBDOMAIN_SEEDS,
)


class DomainSeeder(Seeder):
    model_class = Domain

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'name': Seeder.ordered.choice([seed['name'] for seed in DOMAIN_SEEDS], wrap=True),
        'description': Seeder.ordered.choice(
            [seed['description'] for seed in DOMAIN_SEEDS], wrap=True
        ),
        'sub_domain_description': Seeder.ordered.choice(
            [seed['sub_domain_description'] for seed in DOMAIN_SEEDS], wrap=True
        ),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }


class SubDomainSeeder(Seeder):
    model_class = SubDomain

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'domain_id': Seeder.model.ordered_queryset_foreign_key(Domain.objects.active(), wrap=True),
        'name': Seeder.ordered.choice([seed['name'] for seed in SUBDOMAIN_SEEDS], wrap=True),
        'description': Seeder.ordered.choice(
            [seed['description'] for seed in SUBDOMAIN_SEEDS], wrap=True
        ),
        'key': Seeder.ordered.choice(SUB_DOMAIN_KEYS, wrap=True),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }
