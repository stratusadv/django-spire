from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
from django_spire.knowledge.entry.version.tests.factories import create_test_entry_version


class EntryVersionBlockFactoryServiceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.entry_version = create_test_entry_version()

    def test_create_validated_block_text(self):
        block = EntryVersionBlock.services.factory.create_validated_block(
            entry_version=self.entry_version,
            type=BlockTypeChoices.TEXT,
            data={'text': 'Test content'},
            order=0
        )
        assert block.type == BlockTypeChoices.TEXT
        assert block.order == 0
        assert block._block_data == {'text': 'Test content'}

    def test_create_validated_block_heading(self):
        block = EntryVersionBlock.services.factory.create_validated_block(
            entry_version=self.entry_version,
            type=BlockTypeChoices.HEADING,
            data={'text': 'Title', 'level': 1},
            order=0
        )
        assert block.type == BlockTypeChoices.HEADING
        assert block._block_data['level'] == 1

    def test_create_validated_block_list(self):
        block = EntryVersionBlock.services.factory.create_validated_block(
            entry_version=self.entry_version,
            type=BlockTypeChoices.LIST,
            data={
                'style': 'unordered',
                'items': [{'content': 'Item', 'items': []}]
            },
            order=0
        )
        assert block.type == BlockTypeChoices.LIST

    def test_create_validated_block_with_tunes(self):
        tunes = {'alignment': 'center'}
        block = EntryVersionBlock.services.factory.create_validated_block(
            entry_version=self.entry_version,
            type=BlockTypeChoices.TEXT,
            data={'text': 'Centered'},
            order=0,
            tunes=tunes
        )
        assert block.tunes == tunes

    def test_create_validated_block_sets_version(self):
        block = EntryVersionBlock.services.factory.create_validated_block(
            entry_version=self.entry_version,
            type=BlockTypeChoices.TEXT,
            data={'text': 'Test'},
            order=0
        )
        assert block.version == self.entry_version
