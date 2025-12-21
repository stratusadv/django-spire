from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.tests.factories import create_test_entry
from django_spire.knowledge.entry.version.tests.factories import create_test_entry_version


class EntryServiceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection = create_test_collection()
        self.entry = create_test_entry(collection=self.collection)

    def test_save_model_obj_creates_new_with_version(self):
        entry, created = Entry.services.save_model_obj(
            author=self.super_user,
            name='New Entry',
            collection=self.collection
        )
        assert created is True
        assert entry.name == 'New Entry'
        assert entry.current_version is not None

    def test_save_model_obj_updates_existing(self):
        entry_version = create_test_entry_version(entry=self.entry)
        self.entry.current_version = entry_version
        self.entry.save()

        self.entry.services.obj = self.entry
        updated_entry, created = self.entry.services.save_model_obj(
            author=self.super_user,
            name='Updated Name'
        )
        assert created is False
        assert updated_entry.name == 'Updated Name'


class EntryProcessorServiceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection = create_test_collection()
        self.entry = create_test_entry(collection=self.collection)

    def test_set_deleted(self):
        self.entry.services.processor.set_deleted()
        self.entry.refresh_from_db()
        assert self.entry.is_deleted is True


class EntryToolServiceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection = create_test_collection()
        self.entry = create_test_entry(collection=self.collection)

    def test_get_files_to_convert(self):
        result = Entry.services.tool.get_files_to_convert()
        assert result.count() == 0

    def test_get_files_to_convert_json(self):
        result = Entry.services.tool.get_files_to_convert_json()
        assert result == '[]'


class EntryTransformationServiceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection = create_test_collection()
        self.entry = create_test_entry(collection=self.collection)
        self.entry_version = create_test_entry_version(entry=self.entry)
        self.entry.current_version = self.entry_version
        self.entry.save()

    def test_to_dict(self):
        self.entry.services.transformation.obj = self.entry
        result = self.entry.services.transformation.to_dict()

        assert result['entry_id'] == self.entry.pk
        assert result['name'] == self.entry.name
        assert 'version_id' in result
        assert 'author' in result
        assert 'status' in result
        assert 'delete_url' in result
        assert 'edit_url' in result
        assert 'view_url' in result

    def test_queryset_to_navigation_list(self):
        result = Entry.services.transformation.queryset_to_navigation_list(
            queryset=Entry.objects.filter(pk=self.entry.pk)
        )
        assert len(result) == 1
        assert result[0]['entry_id'] == self.entry.pk
