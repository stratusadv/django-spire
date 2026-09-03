from django_spire.api import models
from django_spire.auth.user.tests.factories import get_default_super_user
from django_spire.contrib.seeding import Seeder


class ApiAccessSeeder(Seeder):
    model_class = models.ApiAccess
    fields_seeds = {'id': Seeder.exclude(), 'name': Seeder.llm(str), 'permission': Seeder.static(1)}

    def __post_seed_database__(self) -> None:
        super_user = get_default_super_user()

        for i, api_access in enumerate(models.ApiAccess.objects.all(), start=1):
            api_access.permission = min(i, 4)
            api_access.user = super_user

            if i == 5:
                api_access.has_super_access = True

            api_access.set_key_and_save(f'stratus{i}')

