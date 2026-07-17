from django_spire.contrib.seeding import Seeder
from test_project.app.ordering.models import Duck


class DuckSeeder(Seeder):
    model_class = Duck
    cache_enabled = True

    fields_seeds = {
        'id': Seeder.exclude(),
        'name': Seeder.fake.first_name(),
        'color': Seeder.llm(field_type=str, prompt='hex color'),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }


duck_seeder = DuckSeeder(count=20)

duck_seeder.seed_database()
