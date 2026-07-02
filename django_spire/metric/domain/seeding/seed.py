from __future__ import annotations

from django_spire.metric.domain.seeding.seeder import DomainSeeder, SubDomainSeeder


DomainSeeder.seed_database(count=10)
SubDomainSeeder.seed_database(count=10)
