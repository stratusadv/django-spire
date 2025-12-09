from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import (
    create_test_collection,
    create_test_collection_group,
)


class CollectionModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection = create_test_collection()

    def test_str(self):
        assert str(self.collection) == self.collection.name

    def test_name_short_truncates(self):
        long_name = 'A' * 100
        collection = create_test_collection(name=long_name)
        assert len(collection.name_short) <= 35

    def test_name_short_no_truncate(self):
        short_name = 'Short'
        collection = create_test_collection(name=short_name)
        assert collection.name_short == short_name

    def test_top_level_parent_returns_self_when_no_parent(self):
        assert self.collection.top_level_parent == self.collection

    def test_top_level_parent_returns_root(self):
        child = create_test_collection(parent=self.collection, name='Child')
        grandchild = create_test_collection(parent=child, name='Grandchild')
        assert grandchild.top_level_parent == self.collection

    def test_base_breadcrumb(self):
        breadcrumbs = self.collection.base_breadcrumb()
        assert breadcrumbs is not None


class CollectionGroupModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection_group = create_test_collection_group()

    def test_str(self):
        expected = f'{self.collection_group.collection.name} - {self.collection_group.auth_group.name}'
        assert str(self.collection_group) == expected
