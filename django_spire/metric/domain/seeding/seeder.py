import os
import random
from time import sleep

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.postgres_settings')
os.environ.setdefault('DANDY_SETTINGS_MODULE', 'test_project.dandy_settings')

application = get_wsgi_application()

from django_spire.contrib.seeder import Seeder
from django_spire.metric.domain.models import Domain, SubDomain


def random_boolean(true_weight: float = 0.5) -> bool:
    number = random.random()
    return number <= true_weight


class DomainSeeder(Seeder):
    model_class = Domain
    cache_enabled = True

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'name': Seeder.fake.sentence(),
        'description': Seeder.llm.automatic(str),
        'sub_domain_description': Seeder.llm.automatic(str),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def __post_seed__(self) -> None:
        sleep(2)

    def __post_seed_database__(self) -> None:
        sleep(2)


domain_seeder = DomainSeeder(count=10)

domain_seeder.seed_database()

print(f'{domain_seeder.queryset.filter(is_deleted=False).count()=}')
print(f'{Domain.objects.all().count()=}')

domain_ids = list(Domain.objects.values_list('id', flat=True))


class SubDomainSeeder(Seeder):
    model_class = SubDomain
    cache_enabled = False

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'domain_id': Seeder.custom.callable(lambda: random.choice(domain_ids)),
        'name': Seeder.fake.sentence(),
        'description': Seeder.llm.automatic(str),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.custom.callable(random_boolean, true_weight=0.4),
    }

    def __post_seed__(self) -> None:
        sleep(2)

    def __post_seed_database__(self) -> None:
        sleep(2)


subdomain_seeder = SubDomainSeeder(count=200)

subdomain_seeder.seed_database()

print(f'{subdomain_seeder.queryset.filter(is_deleted=False).count()=}')
print(f'{SubDomain.objects.all().count()=}')
