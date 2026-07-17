from django_spire.api import models
from django_spire.contrib.seeding import Seeder


class ApiAccessSeeder(Seeder):
    model_class = models.ApiAccess
    fields_seeds = {'id': Seeder.exclude(), 'name': Seeder.llm(str), 'permission': Seeder.static(1)}

    @staticmethod
    def update_hashed_keys() -> None:
        for i, api_access in enumerate(models.ApiAccess.objects.all(), start=1):
            api_access.permission = min(i, 4)
            api_access.set_key_and_save(f'stratus{i}')


api_seeder = ApiAccessSeeder(count=5)

api_seeder.seed_database()

api_seeder.update_hashed_keys()
