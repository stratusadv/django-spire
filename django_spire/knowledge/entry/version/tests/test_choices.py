from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.choices import EntryVersionStatusChoices


class EntryVersionStatusChoicesTests(BaseTestCase):
    def test_draft_value(self):
        assert EntryVersionStatusChoices.DRAFT == 'draft'

    def test_published_value(self):
        assert EntryVersionStatusChoices.PUBLISHED == 'published'

    def test_archived_value(self):
        assert EntryVersionStatusChoices.ARCHIVED == 'archived'

    def test_choices_count(self):
        assert len(EntryVersionStatusChoices.choices) == 3
