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

    def add_update_delete_blocks(self, block_data_list: list[dict]):
        from django_spire.knowledge.entry.version.block.models import EntryVersionBlock

        entry_blocks_to_add = []
        entry_blocks_to_update = []

        handled_block_ids = []

        old_entry_blocks = self.obj.blocks.active()

        old_entry_block_ids = [entry_block.id for entry_block in old_entry_blocks]

        for block_data in block_data_list:
            if block_data['id'] in old_entry_block_ids:
                entry_block: EntryVersionBlock = old_entry_blocks.get(id=block_data['id'])

                entry_block.type = block_data['type']
                entry_block.order = block_data['order']
                entry_block.update_editor_js_block_data_from_dict(block_data['data'])

                entry_blocks_to_update.append(entry_block)

                handled_block_ids.append(block_data['id'])

            else:
                entry_block = EntryVersionBlock.services.factory.create_validated_block(
                    entry_version=self.obj,
                    **block_data,
                )
                entry_blocks_to_add.append(entry_block)

                handled_block_ids.append(block_data['id'])

        entry_blocks_to_delete = [
            entry_block.id
            for entry_block in old_entry_blocks
            if entry_block.id not in handled_block_ids
        ]

        with transaction.atomic():
            EntryVersionBlock.objects.filter(id__in=entry_blocks_to_delete).delete()
            EntryVersionBlock.objects.bulk_update(entry_blocks_to_update, ['order', 'type', '_block_data', '_text_data'])
            EntryVersionBlock.objects.bulk_create(entry_blocks_to_add)

        self.obj.entry.services.search_index.rebuild_search_index()
