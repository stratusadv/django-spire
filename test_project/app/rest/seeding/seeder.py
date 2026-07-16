import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.postgres_settings')
os.environ.setdefault('DANDY_SETTINGS_MODULE', 'test_project.dandy_settings')

application = get_wsgi_application()

from django_spire.contrib.seeding import Seeder
from test_project.app.rest.models import Pirate


class PirateModelSeeder(Seeder):
    model_class = Pirate
    cache_enabled = True

    fields_seeds = {
        'id': Seeder.exclude(),
        'first_name': Seeder.fake.first_name(),
        'last_name': Seeder.fake.last_name(),
        'email': Seeder.llm(field_type=str, prompt='email'),
        'username': Seeder.llm(field_type=str, prompt='username'),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
    }


pirate_model_seeder = PirateModelSeeder(count=50)

pirate_model_seeder.seed_database()
