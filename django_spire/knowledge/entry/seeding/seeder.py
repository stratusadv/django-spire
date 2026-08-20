from __future__ import annotations

from django_spire.contrib.seeding import Seeder
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry import models
from django_spire.knowledge.entry.version.seeding.seeder import EntryVersionSeeder


class EntrySeeder(Seeder):
    model_class = models.Entry

    fields_seeds = {
        'id': Seeder.exclude(),
        'current_version_id': Seeder.exclude(),
        'collection_id': Seeder.model.random_foreign_key(Collection),
        'name': Seeder.llm(
            str, 'A name for a document in a company knowledge base: a policy or process article.'
        ),
    }

    def __post_seed_database__(self) -> None:
        self._correct_order()
        self._set_current_version()

        for entry in self.queryset:
            entry.services.tag.process_and_set_tags()

    def _correct_order(self) -> None:
        for collection in Collection.objects.all():
            collection_entries = collection.entries.all()

            for idx, entry in enumerate(collection_entries):
                entry.order = idx

            self.model_class.objects.bulk_update(collection_entries, ['order'])

    def _set_current_version(self) -> None:
        entries = list(self.queryset)

        entry_version_seeder = EntryVersionSeeder(count=len(entries))
        entry_versions = entry_version_seeder.seed_for_entries(entries=entries)

        for entry, entry_version in zip(entries, entry_versions, strict=False):
            entry.current_version = entry_version

        self.model_class.objects.bulk_update(entries, ['current_version'])
