from __future__ import annotations

import pytest

from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.exceptions import FileValidationError
from django_spire.file.factory import BATCH_SIZE_MAX
from django_spire.file.handlers import MultiFileHandler, SingleFileHandler
from django_spire.file.models import File
from django_spire.file.tests.factories import (
    create_test_file,
    create_test_in_memory_uploaded_file,
)
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket


STORAGES_OVERRIDE = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


@override_settings(STORAGES=STORAGES_OVERRIDE)
class SingleFileHandlerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.handler = SingleFileHandler.for_related_field('pfp')
        self.ticket = create_test_helpdesk_ticket()
        self.content_type = ContentType.objects.get_for_model(self.ticket)

    def test_for_related_field(self) -> None:
        handler = SingleFileHandler.for_related_field('pfp')

        assert handler.factory.related_field == 'pfp'
        assert handler.linker.related_field == 'pfp'

    def test_save_none_returns_none(self) -> None:
        result = self.handler.save(None, self.ticket)

        assert result is None

    def test_save_upload_creates_file(self) -> None:
        initial_count = File.objects.count()
        file = create_test_in_memory_uploaded_file()

        self.handler.save(file, self.ticket)

        assert File.objects.count() == initial_count + 1

    def test_save_upload_links_to_instance(self) -> None:
        file = create_test_in_memory_uploaded_file()

        result = self.handler.save(file, self.ticket)

        assert result.object_id == self.ticket.pk
        assert result.content_type == self.content_type

    def test_save_upload_unlinks_existing(self) -> None:
        old_file = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )

        self.handler.save(create_test_in_memory_uploaded_file(), self.ticket)

        old_file.refresh_from_db()
        assert old_file.is_active is False
        assert old_file.is_deleted is True

    def test_save_ajax_links_existing_file(self) -> None:
        file = create_test_file(name='unlinked')

        result = self.handler.save({'id': file.pk}, self.ticket)

        assert result.pk == file.pk
        result.refresh_from_db()
        assert result.object_id == self.ticket.pk

    def test_save_ajax_returns_already_linked_file(self) -> None:
        file = create_test_file(
            name='linked',
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )

        result = self.handler.save({'id': file.pk}, self.ticket)

        assert result.pk == file.pk

    def test_save_ajax_rejects_file_owned_by_other_object(self) -> None:
        other_ticket = create_test_helpdesk_ticket()
        other_content_type = ContentType.objects.get_for_model(other_ticket)
        file = create_test_file(
            name='owned',
            content_type=other_content_type,
            object_id=other_ticket.pk,
        )

        result = self.handler.save({'id': file.pk}, self.ticket)

        assert result is None
        file.refresh_from_db()
        assert file.object_id == other_ticket.pk

    def test_save_ajax_empty_id_returns_none(self) -> None:
        result = self.handler.save({'id': 0}, self.ticket)

        assert result is None

    def test_save_ajax_missing_id_returns_none(self) -> None:
        result = self.handler.save({}, self.ticket)

        assert result is None

    def test_save_ajax_nonexistent_id_returns_none(self) -> None:
        result = self.handler.save({'id': 999999}, self.ticket)

        assert result is None


@override_settings(STORAGES=STORAGES_OVERRIDE)
class SingleFileHandlerEdgeCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.handler = SingleFileHandler.for_related_field('pfp')
        self.ticket = create_test_helpdesk_ticket()
        self.content_type = ContentType.objects.get_for_model(self.ticket)

    def test_save_unsupported_type_raises(self) -> None:
        with pytest.raises(TypeError, match='Unsupported data type'):
            self.handler.save('not_a_file', self.ticket)

    def test_save_integer_raises(self) -> None:
        with pytest.raises(TypeError, match='Unsupported data type'):
            self.handler.save(42, self.ticket)

    def test_save_ajax_negative_id_returns_none(self) -> None:
        result = self.handler.save({'id': -1}, self.ticket)

        assert result is None

    def test_save_ajax_string_id_returns_none(self) -> None:
        result = self.handler.save({'id': 'abc'}, self.ticket)

        assert result is None

    def test_save_ajax_none_id_returns_none(self) -> None:
        result = self.handler.save({'id': None}, self.ticket)

        assert result is None

    def test_save_ajax_soft_deleted_orphan_is_claimable(self) -> None:
        file = create_test_file(name='deleted_orphan', is_active=False, is_deleted=True)

        result = self.handler.save({'id': file.pk}, self.ticket)

        assert result is not None
        result.refresh_from_db()
        assert result.object_id == self.ticket.pk

    def test_save_ajax_orphan_claimed_by_different_user_context(self) -> None:
        orphan = create_test_file(name='orphan')
        other_ticket = create_test_helpdesk_ticket()
        other_handler = SingleFileHandler.for_related_field('pfp')

        result = other_handler.save({'id': orphan.pk}, other_ticket)

        assert result is not None
        assert result.object_id == other_ticket.pk

        second_result = self.handler.save({'id': orphan.pk}, self.ticket)

        assert second_result is None

    def test_save_upload_twice_only_latest_linked(self) -> None:
        file1 = create_test_in_memory_uploaded_file(name='first')
        file2 = create_test_in_memory_uploaded_file(name='second')

        result1 = self.handler.save(file1, self.ticket)
        result2 = self.handler.save(file2, self.ticket)

        result1.refresh_from_db()
        assert result1.is_active is False
        assert result1.is_deleted is True
        assert result2.is_active is True
        assert result2.object_id == self.ticket.pk

    def test_save_ajax_with_extra_keys_ignored(self) -> None:
        file = create_test_file(name='extra_keys')

        result = self.handler.save(
            {'id': file.pk, 'name': 'evil', 'url': 'https://evil.com'},
            self.ticket,
        )

        assert result is not None
        result.refresh_from_db()
        assert result.name == 'extra_keys'


@override_settings(STORAGES=STORAGES_OVERRIDE)
class MultiFileHandlerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.handler = MultiFileHandler.for_related_field('abc')
        self.ticket = create_test_helpdesk_ticket()
        self.content_type = ContentType.objects.get_for_model(self.ticket)

    def test_for_related_field(self) -> None:
        handler = MultiFileHandler.for_related_field('abc')

        assert handler.factory.related_field == 'abc'
        assert handler.linker.related_field == 'abc'

    def test_save_none_returns_empty_list(self) -> None:
        result = self.handler.save(None, self.ticket)

        assert result == []

    def test_save_empty_list_returns_empty_list(self) -> None:
        result = self.handler.save([], self.ticket)

        assert result == []

    def test_save_upload_creates_files(self) -> None:
        initial_count = File.objects.count()
        files = [
            create_test_in_memory_uploaded_file(name='file1'),
            create_test_in_memory_uploaded_file(name='file2'),
        ]

        self.handler.save(files, self.ticket)

        assert File.objects.count() == initial_count + 2

    def test_save_upload_links_all_to_instance(self) -> None:
        files = [
            create_test_in_memory_uploaded_file(name='file1'),
            create_test_in_memory_uploaded_file(name='file2'),
        ]

        result = self.handler.save(files, self.ticket)

        for file in result:
            assert file.object_id == self.ticket.pk

    def test_save_upload_unlinks_existing(self) -> None:
        old_file = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='abc',
        )

        self.handler.save(
            [create_test_in_memory_uploaded_file()],
            self.ticket,
        )

        old_file.refresh_from_db()
        assert old_file.is_active is False

    def test_save_ajax_links_unlinked_files(self) -> None:
        file1 = create_test_file(name='unlinked1')
        file2 = create_test_file(name='unlinked2')

        result = self.handler.save(
            [{'id': file1.pk}, {'id': file2.pk}],
            self.ticket,
        )

        assert len(result) == 2

    def test_save_ajax_removes_unlisted_files(self) -> None:
        keep = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='abc',
        )
        remove = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='abc',
        )

        self.handler.save([{'id': keep.pk}], self.ticket)

        remove.refresh_from_db()
        assert remove.is_active is False

    def test_save_ajax_rejects_files_owned_by_other_object(self) -> None:
        other_ticket = create_test_helpdesk_ticket()
        other_content_type = ContentType.objects.get_for_model(other_ticket)
        stolen = create_test_file(
            name='stolen',
            content_type=other_content_type,
            object_id=other_ticket.pk,
        )

        result = self.handler.save([{'id': stolen.pk}], self.ticket)

        assert len(result) == 0
        stolen.refresh_from_db()
        assert stolen.object_id == other_ticket.pk

    def test_save_exceeding_batch_size_raises(self) -> None:
        data = [{'id': i} for i in range(BATCH_SIZE_MAX + 1)]

        with pytest.raises(FileValidationError):
            self.handler.save(data, self.ticket)


@override_settings(STORAGES=STORAGES_OVERRIDE)
class MultiFileHandlerEdgeCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.handler = MultiFileHandler.for_related_field('abc')
        self.ticket = create_test_helpdesk_ticket()
        self.content_type = ContentType.objects.get_for_model(self.ticket)

    def test_save_unsupported_element_type_raises(self) -> None:
        with pytest.raises(TypeError, match='Unsupported data element type'):
            self.handler.save(['not_a_file'], self.ticket)

    def test_save_ajax_duplicate_ids(self) -> None:
        file = create_test_file(name='dupe')

        _ = self.handler.save(
            [{'id': file.pk}, {'id': file.pk}],
            self.ticket,
        )

        linked = File.objects.filter(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='abc',
            is_active=True,
        )
        assert linked.count() == 1

    def test_save_ajax_all_nonexistent_ids(self) -> None:
        result = self.handler.save(
            [{'id': 999997}, {'id': 999998}, {'id': 999999}],
            self.ticket,
        )

        assert result == []

    def test_save_ajax_mix_valid_and_invalid_ids(self) -> None:
        valid = create_test_file(name='valid')

        result = self.handler.save(
            [{'id': valid.pk}, {'id': 999999}],
            self.ticket,
        )

        ids = [f.pk for f in result]
        assert valid.pk in ids

    def test_save_ajax_empty_id_in_data_skipped(self) -> None:
        file = create_test_file(name='real')

        result = self.handler.save(
            [{'id': file.pk}, {'id': 0}, {}],
            self.ticket,
        )

        linked = [f for f in result if f.name == 'real']
        assert len(linked) == 1

    def test_save_ajax_soft_deleted_orphan_is_claimable(self) -> None:
        file = create_test_file(name='deleted_orphan', is_active=False, is_deleted=True)

        result = self.handler.save([{'id': file.pk}], self.ticket)

        claimed = [f for f in result if f.pk == file.pk]
        assert len(claimed) == 1

    def test_save_ajax_at_exact_batch_size(self) -> None:
        files = [create_test_file(name=f'f{i}') for i in range(BATCH_SIZE_MAX)]
        data = [{'id': f.pk} for f in files]

        result = self.handler.save(data, self.ticket)

        assert len(result) == BATCH_SIZE_MAX

    def test_save_upload_then_ajax_replaces_all(self) -> None:
        uploads = [
            create_test_in_memory_uploaded_file(name='upload1'),
            create_test_in_memory_uploaded_file(name='upload2'),
        ]
        uploaded = self.handler.save(uploads, self.ticket)

        new_file = create_test_file(name='ajax_file')
        result = self.handler.save([{'id': new_file.pk}], self.ticket)

        for f in uploaded:
            f.refresh_from_db()
            assert f.is_active is False

        assert len(result) == 1

    def test_save_ajax_unlinks_all_when_empty_ids_submitted(self) -> None:
        existing = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='abc',
        )

        self.handler.save([{}, {}], self.ticket)

        existing.refresh_from_db()
        assert existing.is_active is False
