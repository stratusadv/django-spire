from django_spire.contrib.seeding import Seeder
from django_spire.metric.domain.models import Domain, SubDomain


class DomainSeeder(Seeder):
    model_class = Domain

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'name': Seeder.fake.sentence(),
        'description': Seeder.llm(str),
        'sub_domain_description': Seeder.llm(str),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }


class SubDomainSeeder(Seeder):
    model_class = SubDomain

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'domain_id': Seeder.model.random_foreign_key(Domain),
        'name': Seeder.fake.sentence(),
        'description': Seeder.llm(str),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.fake.boolean(),
    }
