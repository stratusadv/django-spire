from __future__ import annotations

from django_spire.api import models

from django_spire.contrib.seeding import DjangoModelSeeder


class ApiAccessSeeder(DjangoModelSeeder):
    model_class = models.ApiAccess
    fields = {
        'id': 'exclude',
        'name': (
            'llm',
            'A Short name to identify an API access key'
        ),
    }

    @staticmethod
    def update_hashed_keys():
        for i, api_access in enumerate(models.ApiAccess.objects.all()):
            api_access.set_key_and_save(
                f'stratus{i}'
            )