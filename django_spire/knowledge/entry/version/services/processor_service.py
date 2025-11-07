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

        entry_blocks_to_add = []
        entry_blocks_to_update = []
        entry_blocks_to_delete = []

        handled_blocks = []

        old_entry_blocks = self.obj.blocks.active()

        old_entry_block_ids = (entry_block.id for entry_block in old_entry_blocks)

        for block_data in raw_block_data:
            if block_data['block_id'] in old_entry_block_ids:
                entry_block: EntryVersionBlock = old_entry_blocks.get(id=block_data['block_id'])
                entry_block.type = block_data['block_type']
                entry_block.order = block_data['block_order']
                entry_block.update_editor_block_data_from_dict(block_data['block_data'])
                entry_blocks_to_update.append(entry_block)

                handled_blocks.append(block_data['block_id'])

            else:
                entry_block = EntryVersionBlock.services.factory.create_validated_block(
                    entry_version=self.obj,
                    **block_data,
                )
                entry_blocks_to_add.append(entry_block)
                handled_blocks.append(block_data['block_id'])

        for entry_block in old_entry_blocks:
            if entry_block.id not in handled_blocks:
                entry_blocks_to_delete.append(entry_block.id)

        # incoming_entry_blocks = [
        #     EntryVersionBlock.services.factory.create_validated_block(
        #         entry_version=self.obj,
        #         **block_data,
        #     )
        #     for block_data in raw_block_data
        # ]

        with transaction.atomic():
            EntryVersionBlock.objects.filter(id__in=entry_blocks_to_delete).delete()
            EntryVersionBlock.objects.bulk_update(entry_blocks_to_update, ['order', 'type', '_block_data', '_text_data'])
            EntryVersionBlock.objects.bulk_create(entry_blocks_to_add)
