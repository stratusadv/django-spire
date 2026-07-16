import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.postgres_settings')
os.environ.setdefault('DANDY_SETTINGS_MODULE', 'test_project.dandy_settings')

application = get_wsgi_application()

from django.contrib.auth.models import User

from django_spire.contrib.seeding import Seeder


class UserSeeder(Seeder):
    model_class = User
    cache_seed = False

    fields_seeds = {
        'id': Seeder.exclude(),
        'username': Seeder.llm(field_type=str, prompt='username'),
        'first_name': Seeder.fake.first_name(),
        'last_name': Seeder.fake.last_name(),
        'email': Seeder.llm(str),
        'is_staff': Seeder.fake.boolean(),
        'is_superuser': Seeder.static(False),
        'is_active': Seeder.static(True),
        'date_joined': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'password': Seeder.exclude(),  # password hash slows down seeding
        'last_login': Seeder.exclude(),
    }


user_seeder = UserSeeder(count=20)

user_seeder.seed_database()

print(f'{User.objects.all().count()=}')
