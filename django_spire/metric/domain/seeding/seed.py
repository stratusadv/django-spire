from __future__ import annotations

from django_spire.metric.domain.seeding.constants import DOMAIN_SEEDS, SUBDOMAIN_SEEDS
from django_spire.metric.domain.seeding.seeder import DomainSeeder, SubDomainSeeder

domain_seeder = DomainSeeder(count=len(DOMAIN_SEEDS))

domain_seeder.seed_database()

subdomain_seeder = SubDomainSeeder(count=len(SUBDOMAIN_SEEDS) * 2)

subdomain_seeder.seed_database()

from django_spire.metric.domain.statistic.seeding.seed import *  # noqa: E402, F403
