from django.contrib.auth.models import User

from django_spire.contrib.seeding import DjangoModelSeeder


class UserSeeder(DjangoModelSeeder):
    model_class = User
    cache_seed = False
    default_to = 'faker'
    fields = {
        'id': 'exclude',
        'username': ('llm', 'A person\'s user name related to name'),
        'first_name': ('llm', 'A person\'s first name'),
        'last_name': ('llm', 'A person\'s last name'),
        'email': ('llm', 'A person\'s email address related to the first and last name'),
        'is_staff': ('faker', 'boolean'),
        'is_superuser': False,
        'is_active': True,
        'date_joined': ('custom', 'date_time_between', {'start_date': '-30d', 'end_date': 'now'}),
        'password': 'exclude',  # password hash slows down seeding
        'last_login': 'exclude'
    }
