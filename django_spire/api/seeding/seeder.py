from __future__ import annotations

from django_spire.api import models
from django_spire.contrib.seeding import DjangoModelSeeder


class ApiAccessSeeder(DjangoModelSeeder):
    model_class = models.ApiAccess
    fields = {
        'id': 'exclude',
        'name': ('llm', 'A Short name to identify an API access key, like a fake client name etc.'),
        'permission': ('static', 1)
    }

    @staticmethod
    def update_hashed_keys() -> None:
        for i, api_access in enumerate(models.ApiAccess.objects.all(), start=1):
            api_access.permission = min(i, 4)
            api_access.set_key_and_save(f'stratus{i}')

