from django.contrib.auth.models import User

from django_spire.contrib.seeding import DjangoModelSeeder


class UserSeeder(DjangoModelSeeder):
    model_class=User
    cache_seed = False

    fields={
        'id': 'exclude',
        'username': ('faker', 'name'),
        'first_name': ('faker', 'first_name'),
        'last_name': ('faker', 'last_name'),
        'email': ('faker', 'email'),
        'is_staff': ('faker', 'boolean'),
        'is_superuser': False,
        'is_active': True,
        'date_joined': ('custom', 'date_time_between', {'start_date': '-30d', 'end_date': 'now'}),
        'password': 'exclude', # password hash slows down seeding
        'last_login': 'exclude'
    }
    default_to = 'faker'
