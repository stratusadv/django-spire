from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection
from django_spire.knowledge.entry.models import Entry


class EntryFactoryServiceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection = create_test_collection()

    def test_create_from_files_empty_list(self):
        entries = Entry.services.factory.create_from_files(
            author=self.super_user,
            collection=self.collection,
            files=[]
        )
        assert entries == []
