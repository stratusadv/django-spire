from django_spire.contrib.seeding import Seeder
from test_project.app.celery.models import CeleryStalk


class CeleryStalkSeeder(Seeder):
    model_class = CeleryStalk
    cache_enabled = True

    fields_seeds = {
        'id': Seeder.exclude(),
        'is_crisp': Seeder.fake.boolean(),
        'length_inches': Seeder.random.float(0, 999.99),
    }


celery_stalk_seeder = CeleryStalkSeeder()

celery_stalk_seeder.seed_database(count=50)
