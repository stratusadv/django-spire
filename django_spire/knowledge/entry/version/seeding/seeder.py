from __future__ import annotations

import random
from datetime import timedelta

from django.utils.timezone import localtime

from django_spire.auth.user.models import AuthUser
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.version import models

from django_spire.contrib.seeding import DjangoModelSeeder
from django_spire.knowledge.entry.version.choices import EntryVersionStatusChoices


class EntryVersionSeeder(DjangoModelSeeder):
    model_class = models.EntryVersion
    # cache_name = 'entry_version_seeder'
    fields = {
        'id': 'exclude',
        'entry_id': ('custom', 'fk_random', {'model_class': Entry}),
        'author_id': ('custom', 'fk_random', {'model_class': AuthUser}),
        'published_datetime': 'exclude',
        'last_edit_datetime': (
            'custom',
            'date_time_between',
            {'start_date': '-30d', 'end_date': 'now'},
        ),
    }

    @classmethod
    def seed_database(
            cls,
            count: int = 1,
            fields: dict | None = None
    ) -> list[models.EntryVersion]:
        entry_versions = super().seed_database(count=count, fields=fields)

        for entry_version in entry_versions:
            if entry_version.status == EntryVersionStatusChoices.PUBLISHED:
                entry_version.published_datetime = localtime() - timedelta(
                    days=random.randint(0, 30), hours=random.randint(0, 23)
                )

        cls.model_class.objects.bulk_update(entry_versions, ['published_datetime'])
        return entry_versions
