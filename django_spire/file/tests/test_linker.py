from __future__ import annotations

import pytest

from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.factory import RELATED_FIELD_LENGTH_MAX
from django_spire.file.linker import FileLinker
from django_spire.file.tests.factories import create_test_file
from django_spire.help_desk.models import HelpDeskTicket
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
class FileLinkerInitTests(BaseTestCase):
    def test_default_related_field(self) -> None:
        linker = FileLinker()

        assert linker.related_field == ''

    def test_related_field_at_max_length(self) -> None:
        linker = FileLinker(related_field='x' * RELATED_FIELD_LENGTH_MAX)

        assert len(linker.related_field) == RELATED_FIELD_LENGTH_MAX

    def test_related_field_exceeding_max_length_raises(self) -> None:
        with pytest.raises(ValueError, match='related_field must not exceed'):
            FileLinker(related_field='x' * (RELATED_FIELD_LENGTH_MAX + 1))


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileLinkerLinkTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.linker = FileLinker(related_field='pfp')
        self.ticket = create_test_helpdesk_ticket()
        self.file = create_test_file()

    def test_link_sets_content_type(self) -> None:
        self.linker.link(self.file, self.ticket)

        expected = ContentType.objects.get_for_model(self.ticket)
        assert self.file.content_type == expected

    def test_link_sets_object_id(self) -> None:
        self.linker.link(self.file, self.ticket)

        assert self.file.object_id == self.ticket.pk

    def test_link_sets_related_field(self) -> None:
        self.linker.link(self.file, self.ticket)

        assert self.file.related_field == 'pfp'

    def test_link_returns_file(self) -> None:
        result = self.linker.link(self.file, self.ticket)

        assert result == self.file

    def test_link_unsaved_instance_raises_value_error(self) -> None:
        unsaved = HelpDeskTicket()

        with pytest.raises(ValueError, match='Cannot link a file to an unsaved'):
            self.linker.link(self.file, unsaved)

    def test_link_overwrites_previous_link(self) -> None:
        ticket1 = create_test_helpdesk_ticket()
        ticket2 = create_test_helpdesk_ticket()

        self.linker.link(self.file, ticket1)
        self.linker.link(self.file, ticket2)

        self.file.refresh_from_db()
        assert self.file.object_id == ticket2.pk

    def test_link_persists_to_database(self) -> None:
        self.linker.link(self.file, self.ticket)

        self.file.refresh_from_db()
        assert self.file.object_id == self.ticket.pk
        assert self.file.related_field == 'pfp'


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileLinkerLinkManyTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.linker = FileLinker(related_field='abc')
        self.ticket = create_test_helpdesk_ticket()

    def test_link_many_sets_fields_on_all(self) -> None:
        file1 = create_test_file(name='file1')
        file2 = create_test_file(name='file2')

        self.linker.link_many([file1, file2], self.ticket)

        file1.refresh_from_db()
        file2.refresh_from_db()
        assert file1.object_id == self.ticket.pk
        assert file2.object_id == self.ticket.pk

    def test_link_many_empty_list(self) -> None:
        self.linker.link_many([], self.ticket)

    def test_link_many_unsaved_instance_raises_value_error(self) -> None:
        unsaved = HelpDeskTicket()
        file = create_test_file()

        with pytest.raises(ValueError, match='Cannot link files to an unsaved'):
            self.linker.link_many([file], unsaved)

    def test_link_many_single_file(self) -> None:
        file = create_test_file()

        self.linker.link_many([file], self.ticket)

        file.refresh_from_db()
        assert file.object_id == self.ticket.pk

    def test_link_many_sets_related_field_on_all(self) -> None:
        file1 = create_test_file(name='f1')
        file2 = create_test_file(name='f2')

        self.linker.link_many([file1, file2], self.ticket)

        file1.refresh_from_db()
        file2.refresh_from_db()
        assert file1.related_field == 'abc'
        assert file2.related_field == 'abc'


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileLinkerUnlinkTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.linker = FileLinker(related_field='pfp')
        self.ticket = create_test_helpdesk_ticket()
        self.content_type = ContentType.objects.get_for_model(self.ticket)

    def test_unlink_existing_soft_deletes(self) -> None:
        file = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )

        self.linker.unlink_existing(self.ticket)

        file.refresh_from_db()
        assert file.is_active is False
        assert file.is_deleted is True

    def test_unlink_existing_returns_count(self) -> None:
        create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )

        result = self.linker.unlink_existing(self.ticket)

        assert result == 1

    def test_unlink_existing_ignores_other_related_fields(self) -> None:
        file = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='abc',
        )

        self.linker.unlink_existing(self.ticket)

        file.refresh_from_db()
        assert file.is_active is True

    def test_unlink_except_keeps_specified_ids(self) -> None:
        keep = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )
        remove = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )

        self.linker.unlink_except(self.ticket, keep_ids=[keep.pk])

        keep.refresh_from_db()
        remove.refresh_from_db()
        assert keep.is_active is True
        assert remove.is_active is False

    def test_unlink_existing_returns_zero_when_none_exist(self) -> None:
        result = self.linker.unlink_existing(self.ticket)

        assert result == 0

    def test_unlink_existing_multiple_files(self) -> None:
        create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )
        create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )

        result = self.linker.unlink_existing(self.ticket)

        assert result == 2

    def test_unlink_existing_skips_already_deleted(self) -> None:
        create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
            is_active=False,
            is_deleted=True,
        )

        result = self.linker.unlink_existing(self.ticket)

        assert result == 0

    def test_unlink_existing_unsaved_instance_raises(self) -> None:
        unsaved = HelpDeskTicket()

        with pytest.raises(ValueError, match='Cannot unlink files from an unsaved'):
            self.linker.unlink_existing(unsaved)

    def test_unlink_except_empty_keep_ids_removes_all(self) -> None:
        file1 = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )
        file2 = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )

        self.linker.unlink_except(self.ticket, keep_ids=[])

        file1.refresh_from_db()
        file2.refresh_from_db()
        assert file1.is_active is False
        assert file2.is_active is False

    def test_unlink_except_nonexistent_keep_id_removes_all(self) -> None:
        file = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )

        self.linker.unlink_except(self.ticket, keep_ids=[999999])

        file.refresh_from_db()
        assert file.is_active is False

    def test_unlink_except_unsaved_instance_raises(self) -> None:
        unsaved = HelpDeskTicket()

        with pytest.raises(ValueError, match='Cannot unlink files from an unsaved'):
            self.linker.unlink_except(unsaved, keep_ids=[])
