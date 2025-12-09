from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.models import EntryVersion
from django_spire.knowledge.entry.version.tests.factories import create_test_entry_version
from django_spire.knowledge.entry.version.block.tests.factories import create_test_version_block


class EntryVersionQuerySetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.entry_version = create_test_entry_version()

    def test_prefetch_blocks(self):
        create_test_version_block(version=self.entry_version)
        result = EntryVersion.objects.prefetch_blocks().get(pk=self.entry_version.pk)
        assert result.blocks.count() == 1

    def test_prefetch_blocks_ordering(self):
        create_test_version_block(version=self.entry_version, order=2)
        create_test_version_block(version=self.entry_version, order=1)

        result = EntryVersion.objects.prefetch_blocks().get(pk=self.entry_version.pk)
        blocks = list(result.blocks.all())

        assert blocks[0].order < blocks[1].order
