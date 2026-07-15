from django_spire.contrib.seeding import DjangoModelSeeder

from test_project.app.ordering.models import Duck


class DuckSeeder(DjangoModelSeeder):
    model_class = Duck
    cache_name = 'duck_seeder'
    default_to = 'faker'
    fields = {
        'id': 'exclude',
        'name': ('faker', 'first_name'),
        'color': ('faker', 'hex_color'),
        'created_datetime': (
            'custom',
            'date_time_between',
            {'start_date': '-30d', 'end_date': 'now'},
        ),
        'is_active': True,
        'is_deleted': False,
    }
