from django_spire.contrib.seeding import Seeder
from test_project.app.ordering.models import Duck


class DuckSeeder(Seeder):
    model_class = Duck

    fields_seeds = {
        'id': Seeder.exclude(),
        'name': Seeder.fake.first_name(),
        'color': Seeder.fake.provider(
            provider_callable='color',
            color_format='hex'
        ),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }
