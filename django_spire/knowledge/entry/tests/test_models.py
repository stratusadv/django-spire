from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection
from django_spire.knowledge.entry.tests.factories import create_test_entry


class EntryModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.collection = create_test_collection()
        self.entry = create_test_entry(collection=self.collection)

    def test_str(self):
        assert str(self.entry) == self.entry.name

    def test_name_short_truncates(self):
        long_name = 'A' * 100
        entry = create_test_entry(name=long_name, collection=self.collection)
        assert len(entry.name_short) <= 35

    def test_name_short_no_truncate(self):
        short_name = 'Short'
        entry = create_test_entry(name=short_name, collection=self.collection)
        assert entry.name_short == short_name

    def test_top_level_collection(self):
        child_collection = create_test_collection(
            parent=self.collection,
            name='Child Collection'
        )
        entry = create_test_entry(collection=child_collection)
        assert entry.top_level_collection == self.collection

    def test_top_level_collection_when_already_top(self):
        assert self.entry.top_level_collection == self.collection

    def test_base_breadcrumb(self):
        breadcrumbs = self.entry.base_breadcrumb()
        assert breadcrumbs is not None
