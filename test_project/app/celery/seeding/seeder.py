from django_spire.contrib.seeding import Seeder
from test_project.app.celery.models import CeleryStalk


class CeleryStalkSeeder(Seeder):
    model_class = CeleryStalk

    fields_seeds = {
        'id': Seeder.exclude(),
        'is_crisp': Seeder.fake.boolean(),
        'length_inches': Seeder.random.float(0, 999.99),
    }
