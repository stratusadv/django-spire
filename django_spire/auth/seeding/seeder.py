from django.contrib.auth.models import User

from django_spire.contrib.seeding import Seeder


class UserSeeder(Seeder):
    model_class = User

    fields_seeds = {
        'id': Seeder.exclude(),
        'username': Seeder.exclude(),
        'first_name': Seeder.fake.first_name(),
        'last_name': Seeder.fake.last_name(),
        'email': Seeder.fake.email(),
        'is_staff': Seeder.fake.boolean(),
        'is_superuser': Seeder.static(False),
        'is_active': Seeder.static(True),
        'date_joined': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'password': Seeder.exclude(),  # password hash slows down seeding
        'last_login': Seeder.exclude(),
    }

    def __post_seed__(self) -> None:
        for seed in self.seeds:
            seed['username'] = seed['email']