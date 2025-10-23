from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction
from django.utils.timezone import localtime

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.knowledge.entry.version.choices import EntryVersionStatusChoices

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.models import EntryVersion


class EntryVersionProcessorService(BaseDjangoModelService['EntryVersion']):
    obj: EntryVersion

    def publish(self):
        self.obj.status = EntryVersionStatusChoices.PUBLISHED
        self.obj.published_datetime = localtime()
        self.obj.save()

    def update_blocks(self, raw_block_data: list[dict]):
        from django_spire.knowledge.entry.version.block.models import EntryVersionBlock

        old_entry_blocks = self.obj.blocks.active()

        incoming_entry_blocks = [
            EntryVersionBlock.services.factory.create_validated_block(
                entry_version=self.obj,
                **block_data,
            )
            for block_data in raw_block_data
        ]

        with transaction.atomic():
            old_entry_blocks.delete()
            EntryVersionBlock.objects.bulk_create(incoming_entry_blocks)
