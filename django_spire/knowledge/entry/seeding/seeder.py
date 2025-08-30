from __future__ import annotations

from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry import models

from django_spire.contrib.seeding import DjangoModelSeeder
from django_spire.knowledge.entry.version.seeding.seeder import EntryVersionSeeder


class EntrySeeder(DjangoModelSeeder):
    model_class = models.Entry
    # cache_name = 'entry_seeder'
    fields = {
        'id': 'exclude',
        'current_version': 'exclude',
        'collection_id': ('custom', 'fk_random', {'model_class': Collection}),
        'name': (
            'llm',
            'A name for a document. Make it fun and give it a theme'
        ),
    }

    @classmethod
    def _correct_order(cls, entries: list[models.Entry]) -> list[models.Entry]:
        for collection in Collection.objects.all():
            for idx, entry in enumerate(collection.entries.all(), start=1):
                entry.order = idx

        cls.model_class.objects.bulk_update(entries, ['order'])
        return entries

    @classmethod
    def seed_database(
            cls,
            count: int = 1,
            fields: dict | None = None
    ) -> list[models.Entry]:
        entries = super().seed_database(
            count=count,
            fields=fields
        )

        cls._correct_order(entries)
        return cls._set_current_version(entries)

    @classmethod
    def _set_current_version(cls, entries: list[models.Entry], count: int = 1):
        entry_versions = EntryVersionSeeder.seed_database(count=count)

        for entry, entry_version in zip(entries, entry_versions):
            entry_version.entry = entry
            entry.current_version = entry_version

        cls.model_class.objects.bulk_update(entries, ['current_version'])
        EntryVersionSeeder.model_class.objects.bulk_update(entry_versions, ['entry'])
        return entries
