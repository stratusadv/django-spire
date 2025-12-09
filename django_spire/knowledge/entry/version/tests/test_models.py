from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.choices import EntryVersionStatusChoices
from django_spire.knowledge.entry.version.tests.factories import create_test_entry_version


class EntryVersionModelTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.entry_version = create_test_entry_version()

    def test_is_published_false_when_draft(self):
        self.entry_version.status = EntryVersionStatusChoices.DRAFT
        assert self.entry_version.is_published() is False

    def test_is_published_true_when_published(self):
        self.entry_version.status = EntryVersionStatusChoices.PUBLISHED
        assert self.entry_version.is_published() is True

    def test_is_published_false_when_archived(self):
        self.entry_version.status = EntryVersionStatusChoices.ARCHIVED
        assert self.entry_version.is_published() is False
