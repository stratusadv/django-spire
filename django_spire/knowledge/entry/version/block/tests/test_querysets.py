from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
from django_spire.knowledge.entry.version.block.tests.factories import create_test_version_block
from django_spire.knowledge.entry.version.tests.factories import create_test_entry_version


class EntryVersionBlockQuerySetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.entry_version = create_test_entry_version()
        self.block1 = create_test_version_block(version=self.entry_version, order=0)
        self.block2 = create_test_version_block(version=self.entry_version, order=1)

    def test_format_for_editor(self):
        result = list(
            EntryVersionBlock.objects
            .filter(version=self.entry_version)
            .format_for_editor()
        )
        assert len(result) == 2
        assert 'id' in result[0]
        assert 'type' in result[0]
        assert 'data' in result[0]
        assert 'tunes' in result[0]

    def test_format_for_editor_ordering(self):
        result = list(
            EntryVersionBlock.objects
            .filter(version=self.entry_version)
            .format_for_editor()
        )
        assert result[0]['id'] == self.block1.id
        assert result[1]['id'] == self.block2.id
