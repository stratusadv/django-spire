from django_spire.contrib.seeding import DjangoModelSeeder
from test_project.app.rest.models import Pirate


class PirateModelSeeder(DjangoModelSeeder):
    model_class = Pirate
    cache_name = 'queryset_pirate_seeder'

    fields = {
        'id': 'exclude',
        'first_name': ('faker', 'first_name'),
        'last_name': ('faker', 'last_name'),
        'email': ('faker', 'email'),
        'username': ('faker', 'user_name'),
        'created_datetime': (
            'custom',
            'date_time_between',
            {'start_date': '-30d', 'end_date': 'now'},
        ),
    }

    default_to = 'faker'
