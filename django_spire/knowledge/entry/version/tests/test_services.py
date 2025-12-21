from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.choices import EntryVersionStatusChoices
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
from django_spire.knowledge.entry.version.block.tests.factories import (
    create_test_block_form_data,
    create_test_version_block,
)
from django_spire.knowledge.entry.version.tests.factories import create_test_entry_version


class EntryVersionProcessorServiceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.entry_version = create_test_entry_version()

    def test_publish(self):
        self.entry_version.services.processor.publish()
        self.entry_version.refresh_from_db()
        assert self.entry_version.status == EntryVersionStatusChoices.PUBLISHED
        assert self.entry_version.published_datetime is not None

    def test_add_update_delete_blocks_add_new(self):
        block_data = create_test_block_form_data(id='new_block_123')
        self.entry_version.services.processor.add_update_delete_blocks([block_data])
        assert EntryVersionBlock.objects.filter(version=self.entry_version).count() == 1

    def test_add_update_delete_blocks_update_existing(self):
        existing_block = create_test_version_block(version=self.entry_version)
        block_data = create_test_block_form_data(
            id=existing_block.id,
            data={'text': 'updated text'}
        )
        self.entry_version.services.processor.add_update_delete_blocks([block_data])

        existing_block.refresh_from_db()
        assert existing_block._block_data['text'] == 'updated text'

    def test_add_update_delete_blocks_delete_missing(self):
        existing_block = create_test_version_block(version=self.entry_version)
        self.entry_version.services.processor.add_update_delete_blocks([])
        assert not EntryVersionBlock.objects.filter(pk=existing_block.pk).exists()

    def test_add_update_delete_blocks_mixed_operations(self):
        existing_block = create_test_version_block(version=self.entry_version)
        block_to_delete = create_test_version_block(version=self.entry_version, order=2)

        block_data_update = create_test_block_form_data(
            id=existing_block.id,
            order=0,
            data={'text': 'updated'}
        )
        block_data_new = create_test_block_form_data(id='new_block', order=1)

        self.entry_version.services.processor.add_update_delete_blocks([
            block_data_update,
            block_data_new
        ])

        assert EntryVersionBlock.objects.filter(version=self.entry_version).count() == 2
        assert not EntryVersionBlock.objects.filter(pk=block_to_delete.pk).exists()
