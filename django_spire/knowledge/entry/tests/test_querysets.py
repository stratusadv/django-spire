from __future__ import annotations

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.tests.factories import create_test_entry
from django_spire.knowledge.entry.version.choices import EntryVersionStatusChoices
from django_spire.knowledge.entry.version.tests.factories import create_test_entry_version


class EntryQuerySetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = create_user(username='test_entry_queryset_user')
        self.collection = create_test_collection()
        self.entry = create_test_entry(collection=self.collection)
        self.entry_version = create_test_entry_version(entry=self.entry)
        self.entry.current_version = self.entry_version
        self.entry.save()

    def test_has_current_version(self):
        result = Entry.objects.has_current_version()
        assert self.entry in result

    def test_has_current_version_excludes_none(self):
        entry_without_version = create_test_entry(
            collection=self.collection,
            name='No Version'
        )
        result = Entry.objects.has_current_version()
        assert entry_without_version not in result

    def test_id_in(self):
        entry2 = create_test_entry(collection=self.collection, name='Entry 2')
        result = Entry.objects.id_in([self.entry.pk, entry2.pk])
        assert self.entry in result
        assert entry2 in result

    def test_user_has_access_published(self):
        self.entry_version.status = EntryVersionStatusChoices.PUBLISHED
        self.entry_version.save()

        result = Entry.objects.user_has_access(user=self.user)
        assert self.entry in result

    def test_user_has_access_draft_own(self):
        self.entry_version.status = EntryVersionStatusChoices.DRAFT
        self.entry_version.author = self.user
        self.entry_version.save()

        result = Entry.objects.user_has_access(user=self.user)
        assert self.entry in result

    def test_user_has_access_draft_other(self):
        other_user = create_user(username='other_user')
        self.entry_version.status = EntryVersionStatusChoices.DRAFT
        self.entry_version.author = other_user
        self.entry_version.save()

        result = Entry.objects.user_has_access(user=self.user)
        assert self.entry not in result

    def test_get_by_version_block_id(self):
        from django_spire.knowledge.entry.version.block.tests.factories import (
            create_test_version_block,
        )

        version_block = create_test_version_block(version=self.entry_version)
        result = Entry.objects.get_by_version_block_id(version_block_id=version_block.pk)
        assert result == self.entry
