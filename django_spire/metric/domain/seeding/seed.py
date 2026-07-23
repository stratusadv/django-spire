from __future__ import annotations

from django_spire.metric.domain.seeding.seeder import DomainSeeder, SubDomainSeeder


domain_seeder = DomainSeeder(count=5)

domain_seeder.seed_database()


subdomain_seeder = SubDomainSeeder(count=1000)

subdomain_seeder.seed_database()
