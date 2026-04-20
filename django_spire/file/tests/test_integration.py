from __future__ import annotations

import json

from unittest.mock import patch

import pytest

from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.exceptions import FileValidationError
from django_spire.file.factory import FileFactory, BATCH_SIZE_MAX
from django_spire.file.fields import SingleFileField
from django_spire.file.handlers import MultiFileHandler, SingleFileHandler
from django_spire.file.linker import FileLinker
from django_spire.file.models import File
from django_spire.file.services import copy_files_to_instance
from django_spire.file.tests.factories import (
    create_test_file,
    create_test_in_memory_uploaded_file,
)
from django_spire.file.utils import format_size, parse_extension, parse_name
from django_spire.file.views import file_upload_ajax_multiple, file_upload_ajax_single
from django_spire.file.widgets import MultipleFileWidget, SingleFileWidget
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
class MultiFileHandlerMixedTypeTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.handler = MultiFileHandler.for_related_field('abc')
        self.ticket = create_test_helpdesk_ticket()

    def test_dict_then_upload_crashes_in_ajax_path(self) -> None:
        data = [
            {'id': 1},
            create_test_in_memory_uploaded_file(name='upload'),
        ]

        with pytest.raises((TypeError, AttributeError, KeyError)):
            self.handler.replace(data, self.ticket)

    def test_upload_then_dict_crashes_in_upload_path(self) -> None:
        data = [
            create_test_in_memory_uploaded_file(name='upload'),
            {'id': 1},
        ]

        with pytest.raises((FileValidationError, AttributeError, TypeError)):
            self.handler.replace(data, self.ticket)

    def test_none_element_in_list_crashes(self) -> None:
        data = [
            create_test_in_memory_uploaded_file(name='good'),
            None,
        ]

        with pytest.raises((FileValidationError, AttributeError, TypeError)):
            self.handler.replace(data, self.ticket)

    def test_integer_element_detected_by_type_check(self) -> None:
        with pytest.raises(TypeError, match='Unsupported data element type'):
            self.handler.replace([42], self.ticket)

    def test_string_element_detected_by_type_check(self) -> None:
        with pytest.raises(TypeError, match='Unsupported data element type'):
            self.handler.replace(['file.pdf'], self.ticket)


@override_settings(STORAGES=STORAGES_OVERRIDE)
class HandlerAtomicityTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.ticket = create_test_helpdesk_ticket()
        self.content_type = ContentType.objects.get_for_model(self.ticket)

    def test_multi_upload_unlinks_before_create_many_failure(self) -> None:
        handler = MultiFileHandler.for_related_field('abc')
        existing = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='abc',
        )

        good = create_test_in_memory_uploaded_file(name='good')
        bad = create_test_in_memory_uploaded_file(name='bad', file_type='exe')

        with pytest.raises(FileValidationError):
            handler.replace([good, bad], self.ticket)

        existing.refresh_from_db()
        assert existing.is_active is False

    def test_multi_ajax_unlinks_before_link_many_failure(self) -> None:
            handler = MultiFileHandler.for_related_field('abc')
            existing = create_test_file(
                content_type=self.content_type,
                object_id=self.ticket.pk,
                related_field='abc',
            )
            orphan = create_test_file(name='orphan')

            with (
                patch.object(FileLinker, 'link_many', side_effect=RuntimeError('db error')),
                pytest.raises(RuntimeError),
            ):
                handler.replace([{'id': orphan.pk}], self.ticket)

            existing.refresh_from_db()
            assert existing.is_active is False

    def test_single_upload_unlinks_before_create_failure(self) -> None:
        handler = SingleFileHandler.for_related_field('pfp')
        existing = create_test_file(
            content_type=self.content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )
        bad = create_test_in_memory_uploaded_file(name='bad', file_type='exe')

        with pytest.raises(FileValidationError):
            handler.replace(bad, self.ticket)

        existing.refresh_from_db()
        assert existing.is_active is False


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileModelMissingStorageTests(BaseTestCase):
    def test_to_dict_crashes_when_file_field_is_empty(self) -> None:
        file_obj = File.objects.create(name='ghost', type='pdf', size=0)

        with pytest.raises(ValueError):  # noqa: PT011
            file_obj.to_dict()

    def test_to_json_crashes_when_file_field_is_empty(self) -> None:
        file_obj = File.objects.create(name='ghost', type='pdf', size=0)

        with pytest.raises(ValueError):  # noqa: PT011
            file_obj.to_json()

    def test_formatted_size_works_without_storage_file(self) -> None:
        file_obj = File.objects.create(name='ghost', type='pdf', size=1024)

        assert file_obj.formatted_size == '1.0 KB'


@override_settings(STORAGES=STORAGES_OVERRIDE)
class CopyFilesToInstanceTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.source_ticket = create_test_helpdesk_ticket()
        self.target_ticket = create_test_helpdesk_ticket()
        self.content_type = ContentType.objects.get_for_model(self.source_ticket)

    def test_copy_to_unsaved_instance_raises(self) -> None:
        unsaved = HelpDeskTicket()

        with pytest.raises(ValueError, match='Cannot copy files to an unsaved'):
            copy_files_to_instance(File.objects.none(), unsaved)

    def test_copy_empty_queryset_returns_empty(self) -> None:
        result = copy_files_to_instance(File.objects.none(), self.target_ticket)

        assert result == []

    def test_copy_preserves_name_type_size(self) -> None:
        source = create_test_file(
            name='original',
            file_type='pdf',
            size=12345,
            content_type=self.content_type,
            object_id=self.source_ticket.pk,
        )

        result = copy_files_to_instance(
            File.objects.filter(pk=source.pk),
            self.target_ticket,
        )

        assert len(result) == 1
        copy = result[0]
        assert copy.name == 'original'
        assert copy.type == 'pdf'
        assert copy.size == 12345
        assert copy.pk != source.pk

    def test_copy_preserves_related_field(self) -> None:
        source = create_test_file(
            content_type=self.content_type,
            object_id=self.source_ticket.pk,
            related_field='pfp',
        )

        result = copy_files_to_instance(
            File.objects.filter(pk=source.pk),
            self.target_ticket,
        )

        assert result[0].related_field == 'pfp'

    def test_copy_links_to_target_not_source(self) -> None:
        source = create_test_file(
            content_type=self.content_type,
            object_id=self.source_ticket.pk,
        )

        target_ct = ContentType.objects.get_for_model(self.target_ticket)
        result = copy_files_to_instance(
            File.objects.filter(pk=source.pk),
            self.target_ticket,
        )

        assert result[0].content_type == target_ct
        assert result[0].object_id == self.target_ticket.pk

    def test_copy_does_not_modify_source(self) -> None:
        source = create_test_file(
            content_type=self.content_type,
            object_id=self.source_ticket.pk,
        )
        original_pk = source.pk

        copy_files_to_instance(
            File.objects.filter(pk=source.pk),
            self.target_ticket,
        )

        source.refresh_from_db()
        assert source.pk == original_pk
        assert source.object_id == self.source_ticket.pk

    def test_copy_multiple_files(self) -> None:
        create_test_file(
            name='file1',
            content_type=self.content_type,
            object_id=self.source_ticket.pk,
        )
        create_test_file(
            name='file2',
            content_type=self.content_type,
            object_id=self.source_ticket.pk,
        )

        result = copy_files_to_instance(
            File.objects.filter(
                content_type=self.content_type,
                object_id=self.source_ticket.pk,
            ),
            self.target_ticket,
        )

        assert len(result) == 2


@override_settings(STORAGES=STORAGES_OVERRIDE)
class SingleFileFieldQuerySetTests(BaseTestCase):
    def test_prepare_value_queryset_ordering_matters(self) -> None:
        field = SingleFileField()
        file1 = create_test_file(name='alpha')
        file2 = create_test_file(name='beta')

        result_asc = field.prepare_value(
            File.objects.filter(pk__in=[file1.pk, file2.pk]).order_by('pk')
        )
        result_desc = field.prepare_value(
            File.objects.filter(pk__in=[file1.pk, file2.pk]).order_by('-pk')
        )

        assert json.loads(result_asc)['name'] == 'alpha'
        assert json.loads(result_desc)['name'] == 'beta'

    def test_prepare_value_deleted_file_in_queryset(self) -> None:
        field = SingleFileField()
        file = create_test_file(name='deleted', is_active=False, is_deleted=True)

        result = field.prepare_value(File.objects.filter(pk=file.pk))
        parsed = json.loads(result)

        assert parsed['name'] == 'deleted'


@override_settings(STORAGES=STORAGES_OVERRIDE)
class WidgetToHandlerTypeConfusionTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.ticket = create_test_helpdesk_ticket()

    def test_single_widget_integer_flows_to_handler_raises(self) -> None:
        widget = SingleFileWidget()
        data = {'file_data': json.dumps(42)}

        value = widget.value_from_datadict(data, None, 'file')

        handler = SingleFileHandler.for_related_field('pfp')
        with pytest.raises(TypeError, match='Unsupported data type'):
            handler.replace(value, self.ticket)

    def test_single_widget_string_flows_to_handler_raises(self) -> None:
        widget = SingleFileWidget()
        data = {'file_data': json.dumps('malicious')}

        value = widget.value_from_datadict(data, None, 'file')

        handler = SingleFileHandler.for_related_field('pfp')
        with pytest.raises(TypeError, match='Unsupported data type'):
            handler.replace(value, self.ticket)

    def test_single_widget_list_flows_to_handler_raises(self) -> None:
        widget = SingleFileWidget()
        data = {'file_data': json.dumps([1, 2, 3])}

        value = widget.value_from_datadict(data, None, 'file')

        handler = SingleFileHandler.for_related_field('pfp')
        with pytest.raises(TypeError, match='Unsupported data type'):
            handler.replace(value, self.ticket)

    def test_multi_widget_string_flows_to_handler_crashes(self) -> None:
        widget = MultipleFileWidget()
        data = {'files_data': json.dumps('not a list')}

        value = widget.value_from_datadict(data, None, 'files')

        handler = MultiFileHandler.for_related_field('abc')

        with pytest.raises((TypeError, AttributeError)):
            handler.replace(value, self.ticket)

    def test_multi_widget_dict_flows_to_handler_crashes_with_key_error(self) -> None:
        widget = MultipleFileWidget()
        data = {'files_data': json.dumps({'id': 1})}

        value = widget.value_from_datadict(data, None, 'files')

        handler = MultiFileHandler.for_related_field('abc')

        with pytest.raises(KeyError):
            handler.replace(value, self.ticket)

    def test_multi_widget_nested_none_in_list(self) -> None:
        widget = MultipleFileWidget()
        data = {'files_data': json.dumps([None, {'id': 1}])}

        value = widget.value_from_datadict(data, None, 'files')

        handler = MultiFileHandler.for_related_field('abc')

        with pytest.raises((TypeError, AttributeError)):
            handler.replace(value, self.ticket)


class FormatSizeConsistencyTests(BaseTestCase):
    def test_exact_half_kb(self) -> None:
        assert format_size(512) == '0.5 KB'

    def test_one_third_kb_rounding(self) -> None:
        result = format_size(341)
        value = float(result.split()[0])

        assert value == round(341 / 1024, 2)

    def test_just_under_mb_has_many_digits(self) -> None:
        result = format_size(1_048_575)
        value_str = result.split()[0]

        assert '.' in value_str

    def test_exact_100_mb(self) -> None:
        result = format_size(104_857_600)

        assert result == '100.0 MB'

    def test_fractional_gb(self) -> None:
        result = format_size(1_610_612_736)

        assert 'GB' in result

    def test_very_large_tb(self) -> None:
        result = format_size(5 * 1_099_511_627_776)

        assert 'TB' in result
        assert float(result.split()[0]) == 5.0

    def test_single_byte_decimal_places(self) -> None:
        result = format_size(1)
        value_str = result.split()[0]

        assert value_str == '0.0'

    def test_ten_bytes_decimal_places(self) -> None:
        result = format_size(10)
        value_str = result.split()[0]

        assert value_str == '0.01'


class ParseNameAdversarialTests(BaseTestCase):
    def test_only_dots(self) -> None:
        assert parse_name('...') == '..'

    def test_very_long_name(self) -> None:
        name = 'a' * 10_000 + '.pdf'
        result = parse_name(name)

        assert len(result) == 10_000

    def test_newline_in_name(self) -> None:
        result = parse_name('file\nname.pdf')

        assert result == 'file\nname'

    def test_tab_in_name(self) -> None:
        result = parse_name('file\tname.pdf')

        assert result == 'file\tname'

    def test_carriage_return_in_name(self) -> None:
        result = parse_name('file\rname.pdf')

        assert result == 'file\rname'

    def test_space_only_name(self) -> None:
        result = parse_name(' .pdf')

        assert result == ' '

    def test_unicode_rtl_override_in_name(self) -> None:
        result = parse_name('file\u202Efdp.exe')

        assert '\u202E' in result


class ParseExtensionAdversarialTests(BaseTestCase):
    def test_very_long_extension(self) -> None:
        ext = 'x' * 10_000
        result = parse_extension(f'file.{ext}')

        assert len(result) == 10_000

    def test_newline_in_extension(self) -> None:
        result = parse_extension('file.pd\nf')

        assert result == 'pd\nf'

    def test_unicode_rtl_override_in_extension(self) -> None:
        result = parse_extension('file.\u202Eexe')

        assert '\u202E' in result

    def test_extension_with_only_whitespace(self) -> None:
        result = parse_extension('file.   ')

        assert result == '   '


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileLinkerEdgeCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.linker = FileLinker(related_field='pfp')
        self.ticket = create_test_helpdesk_ticket()

    def test_link_same_file_twice_to_same_instance_is_idempotent(self) -> None:
        file = create_test_file()

        self.linker.link(file, self.ticket)
        self.linker.link(file, self.ticket)

        file.refresh_from_db()
        assert file.object_id == self.ticket.pk
        assert File.objects.filter(pk=file.pk).count() == 1

    def test_link_many_empty_list_does_not_query(self) -> None:
        with self.assertNumQueries(0):
            self.linker.link_many([], self.ticket)

    def test_unlink_existing_only_affects_matching_related_field(self) -> None:
        content_type = ContentType.objects.get_for_model(self.ticket)
        pfp_file = create_test_file(
            content_type=content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )
        other_file = create_test_file(
            content_type=content_type,
            object_id=self.ticket.pk,
            related_field='banner',
        )

        self.linker.unlink_existing(self.ticket)

        pfp_file.refresh_from_db()
        other_file.refresh_from_db()
        assert pfp_file.is_active is False
        assert other_file.is_active is True

    def test_unlink_except_with_very_large_keep_ids(self) -> None:
        content_type = ContentType.objects.get_for_model(self.ticket)
        file = create_test_file(
            content_type=content_type,
            object_id=self.ticket.pk,
            related_field='pfp',
        )

        keep_ids = list(range(1, 1001))
        keep_ids.append(file.pk)

        self.linker.unlink_except(self.ticket, keep_ids=keep_ids)

        file.refresh_from_db()
        assert file.is_active is True

    def test_link_reactivates_soft_deleted_file(self) -> None:
        file = create_test_file(is_active=False, is_deleted=True)

        self.linker.link(file, self.ticket)

        file.refresh_from_db()
        assert file.is_active is True
        assert file.is_deleted is False


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FactoryStorageOrphanTests(BaseTestCase):
    def test_bulk_create_failure_leaves_storage_orphans(self) -> None:
        factory = FileFactory()
        files = [
            create_test_in_memory_uploaded_file(name='file1'),
            create_test_in_memory_uploaded_file(name='file2'),
        ]

        with patch.object(
            File.objects, 'bulk_create', side_effect=RuntimeError('db down')
        ), pytest.raises(RuntimeError):
            factory.create_many(files)


@override_settings(STORAGES=STORAGES_OVERRIDE)
class ViewEdgeCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()

    def test_single_upload_oversized_file_returns_error(self) -> None:
        content = b'x' * (10 * 1024 * 1024 + 1)
        file = create_test_in_memory_uploaded_file(content=content)

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = file
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_multiple_upload_one_oversized_returns_error(self) -> None:
        good = create_test_in_memory_uploaded_file(name='good')
        content = b'x' * (10 * 1024 * 1024 + 1)
        bad = create_test_in_memory_uploaded_file(content=content)

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': ''},
        )
        request.FILES['file1'] = good
        request.FILES['file2'] = bad
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_related_field_with_unicode_returns_error(self) -> None:
        file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': 'документ'},
        )
        request.FILES['file'] = file
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_related_field_with_spaces_returns_error(self) -> None:
        file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': 'has space'},
        )
        request.FILES['file'] = file
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_related_field_with_dots_returns_error(self) -> None:
        file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': 'field.name'},
        )
        request.FILES['file'] = file
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_related_field_with_hyphen_returns_error(self) -> None:
        file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': 'field-name'},
        )
        request.FILES['file'] = file
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_multiple_upload_exceeding_batch_size_returns_error(self) -> None:
        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': ''},
        )

        for i in range(BATCH_SIZE_MAX + 1):
            request.FILES[f'file{i}'] = create_test_in_memory_uploaded_file(
                name=f'file{i}'
            )

        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'


@override_settings(STORAGES=STORAGES_OVERRIDE)
class QuerySetORMEdgeCaseTests(BaseTestCase):
    def test_active_with_values_list(self) -> None:
        file = create_test_file(name='active_file')

        ids = list(File.objects.active().values_list('id', flat=True))

        assert file.pk in ids

    def test_active_with_count(self) -> None:
        create_test_file()
        create_test_file(is_deleted=True)

        assert File.objects.active().count() == 1

    def test_related_field_with_values(self) -> None:
        create_test_file(related_field='pfp')
        create_test_file(related_field='banner')

        names = list(
            File.objects.related_field('pfp').values_list('related_field', flat=True)
        )

        assert all(n == 'pfp' for n in names)

    def test_active_then_delete_via_queryset(self) -> None:
        file = create_test_file()

        File.objects.active().filter(pk=file.pk).delete()

        assert not File.objects.filter(pk=file.pk).exists()

    def test_active_excludes_both_flags_independently(self) -> None:
        only_inactive = create_test_file(is_active=False, is_deleted=False)
        only_deleted = create_test_file(is_active=True, is_deleted=True)
        both = create_test_file(is_active=False, is_deleted=True)
        neither = create_test_file(is_active=True, is_deleted=False)

        active_pks = set(File.objects.active().values_list('pk', flat=True))

        assert only_inactive.pk not in active_pks
        assert only_deleted.pk not in active_pks
        assert both.pk not in active_pks
        assert neither.pk in active_pks
