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
        from django_spire.knowledge.entry.version.block.entities import EditorBlock
        from django_spire.knowledge.entry.version.block.models import EntryVersionBlock

        old_entry_blocks = self.obj.blocks.active()

        incoming_editor_blocks = [EditorBlock(**block) for block in raw_block_data]
        incoming_entry_blocks = [
            EntryVersionBlock.services.factory.from_editor_block(
                editor_block=editor_block,
                entry_version=self.obj
            )
            for editor_block in incoming_editor_blocks
        ]

        with transaction.atomic():
            old_entry_blocks.delete()
            EntryVersionBlock.objects.bulk_create(incoming_entry_blocks)
