import os
import random

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.postgres_settings')
os.environ.setdefault('DANDY_SETTINGS_MODULE', 'test_project.dandy_settings')

application = get_wsgi_application()

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
