from __future__ import annotations

import random

from datetime import timedelta
from typing import TYPE_CHECKING

from django.utils.timezone import localtime

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.seeding import Seeder
from django_spire.knowledge.entry.version import models
from django_spire.knowledge.entry.version.block.data.maps import EDITOR_JS_BLOCK_DATA_REVERSE_MAP
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
from django_spire.knowledge.entry.version.block.seeding.constants import KB_ARTICLES
from django_spire.knowledge.entry.version.choices import EntryVersionStatusChoices

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry


class EntryVersionSeeder(Seeder):
    model_class = models.EntryVersion

    fields_seeds = {
        'id': Seeder.exclude(),
        'entry_id': Seeder.exclude(),
        'author_id': Seeder.model.random_foreign_key(AuthUser),
        'status': Seeder.model.random_field_choice(EntryVersionStatusChoices),
        'last_edit_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def seed_for_entries(self, entries: list[Entry]) -> list[models.EntryVersion]:
        self.seed(count=len(entries))

        entry_versions = self.to_model_instances()

        for entry, entry_version in zip(entries, entry_versions, strict=False):
            entry_version.entry = entry

        self.model_class.objects.bulk_create(entry_versions)
        self._model_object_ids = [entry_version.id for entry_version in entry_versions]

        self._set_published_datetimes()
        self._seed_blocks()

        return entry_versions

    def _set_published_datetimes(self) -> None:
        entry_versions = list(self.queryset)

        for entry_version in entry_versions:
            if entry_version.status == EntryVersionStatusChoices.PUBLISHED:
                entry_version.published_datetime = localtime() - timedelta(
                    days=random.randint(0, 30), hours=random.randint(0, 23)
                )

        self.model_class.objects.bulk_update(entry_versions, ['published_datetime'])

    def _seed_blocks(self) -> None:
        version_blocks: list[EntryVersionBlock] = []

        for entry_version in self.queryset:
            blocks_data = random.choice(KB_ARTICLES)

            for idx, block_data in enumerate(blocks_data):
                version_block = EntryVersionBlock(
                    version=entry_version,
                    type=EDITOR_JS_BLOCK_DATA_REVERSE_MAP[type(block_data)],
                    order=idx,
                )
                version_block.editor_js_block_data = block_data
                version_blocks.append(version_block)

        EntryVersionBlock.objects.bulk_create(version_blocks)
