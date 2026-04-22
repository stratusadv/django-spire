from __future__ import annotations

import json
import pytest

from django.core.exceptions import SuspiciousFileOperation
from django.test import RequestFactory, override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.exceptions import FileValidationError
from django_spire.file.factory import FileFactory
from django_spire.file.handlers import MultiFileHandler, SingleFileHandler
from django_spire.file.linker import FileLinker
from django_spire.file.models import File
from django_spire.file.path import FilePathBuilder
from django_spire.file.tests.factories import (
    create_test_file,
    create_test_in_memory_uploaded_file,
)
from django_spire.file.validators import FileValidator
from django_spire.file.views import file_upload_ajax_single
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
class PathTraversalBypassingViewsTests(BaseTestCase):
    def test_factory_accepts_path_traversal_in_related_field(self) -> None:
        factory = FileFactory(related_field='../../etc')

        assert factory.related_field == '../../etc'

    def test_linker_accepts_path_traversal_in_related_field(self) -> None:
        linker = FileLinker(related_field='../../etc')

        assert linker.related_field == '../../etc'

    def test_handler_accepts_path_traversal_in_related_field(self) -> None:
        handler = SingleFileHandler.for_related_field('../../etc')

        assert handler.factory.related_field == '../../etc'

    def test_factory_create_with_traversal_blocked_by_django(self) -> None:
        factory = FileFactory(related_field='../../etc')
        file = create_test_in_memory_uploaded_file()

        with pytest.raises(SuspiciousFileOperation):
            factory.create(file)

    def test_path_builder_does_not_sanitize_related_field(self) -> None:
        builder = FilePathBuilder(base_folder='uploads', app_name='App')
        path = builder.build('file', 'txt', related_field='../../etc')

        assert '../../etc' in path

    def test_path_builder_does_not_sanitize_app_name(self) -> None:
        builder = FilePathBuilder(base_folder='uploads', app_name='../../etc')
        path = builder.build('file', 'txt')

        assert '../../etc' in path

    def test_path_builder_does_not_sanitize_name(self) -> None:
        builder = FilePathBuilder(base_folder='uploads', app_name='App')
        path = builder.build('../../etc/passwd', 'txt')

        assert '../../etc/passwd' in path

    def test_factory_allows_backslash_traversal_in_related_field(self) -> None:
        factory = FileFactory(related_field='..\\..\\etc')

        assert factory.related_field == '..\\..\\etc'

    def test_multi_handler_accepts_path_traversal(self) -> None:
        handler = MultiFileHandler.for_related_field('../../../tmp')

        assert handler.factory.related_field == '../../../tmp'


@override_settings(STORAGES=STORAGES_OVERRIDE)
class OrphanFileClaimIDORTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.ticket_a = create_test_helpdesk_ticket()
        self.ticket_b = create_test_helpdesk_ticket()

    def test_single_handler_rejects_orphan_without_token(self) -> None:
        orphan = create_test_file(name='user_a_upload')

        handler_b = SingleFileHandler.for_related_field('pfp')
        result = handler_b.replace({'id': orphan.pk}, self.ticket_b)

        assert result is None

    def test_multi_handler_rejects_orphan_without_token(self) -> None:
        orphan = create_test_file(name='user_a_upload')

        handler_b = MultiFileHandler.for_related_field('abc')
        result = handler_b.replace([{'id': orphan.pk}], self.ticket_b)

        assert len(result) == 0

    def test_sequential_id_guessing_blocked_without_tokens(self) -> None:
        orphans = [create_test_file(name=f'orphan_{i}') for i in range(5)]

        handler = SingleFileHandler.for_related_field('pfp')
        claimed_count = 0

        for orphan in orphans:
            result = handler.replace({'id': orphan.pk}, self.ticket_b)
            if result is not None:
                claimed_count += 1

        assert claimed_count == 0

    def test_soft_deleted_orphan_rejected_without_token(self) -> None:
        orphan = create_test_file(
            name='deleted_by_user_a',
            is_active=False,
            is_deleted=True,
        )

        handler = SingleFileHandler.for_related_field('pfp')
        result = handler.replace({'id': orphan.pk}, self.ticket_b)

        assert result is None


class NullByteInjectionTests(BaseTestCase):
    def test_null_byte_before_extension_rejected(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = 'payload.\x00exe'

        with pytest.raises(FileValidationError, match='null bytes'):
            validator.validate(file)

    def test_null_byte_after_extension_dot_rejected(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = 'payload.exe\x00.pdf'

        with pytest.raises(FileValidationError, match='null bytes'):
            validator.validate(file)

    def test_null_byte_mid_extension_rejected(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = 'payload.ex\x00e'

        with pytest.raises(FileValidationError, match='null bytes'):
            validator.validate(file)

    def test_null_byte_in_name_rejected(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = 'pay\x00load.pdf'

        with pytest.raises(FileValidationError, match='null bytes'):
            validator.validate(file)


@override_settings(STORAGES=STORAGES_OVERRIDE)
class ValidatorFactoryConsistencyTests(BaseTestCase):
    def test_env_file_rejected_by_validator(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = '.env'

        with pytest.raises(FileValidationError, match='File must have an extension'):
            validator.validate(file)

    def test_trailing_dot_rejected_by_validator(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = 'Makefile.'

        with pytest.raises(FileValidationError, match='File must have an extension'):
            validator.validate(file)

    def test_double_dot_blocked_by_django_before_reaching_factory(self) -> None:
        file = create_test_in_memory_uploaded_file()

        with pytest.raises(SuspiciousFileOperation):
            file.name = '..'

    def test_triple_dot_rejected_by_validator(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = '...'

        with pytest.raises(FileValidationError, match='File must have an extension'):
            validator.validate(file)

    def test_create_many_dotfile_rejected_by_validator(self) -> None:
        factory = FileFactory()
        good = create_test_in_memory_uploaded_file(name='good')
        bad = create_test_in_memory_uploaded_file()
        bad.name = '.gitignore'

        initial_count = File.objects.count()

        with pytest.raises(FileValidationError, match='File must have an extension'):
            factory.create_many([good, bad])

        assert File.objects.count() == initial_count

    def test_view_upload_dotfile_returns_error(self) -> None:
        rf = RequestFactory()
        file = create_test_in_memory_uploaded_file()
        file.name = '.dockerignore'

        request = rf.post('/upload/single/ajax', data={'related_field': ''})
        request.FILES['file'] = file
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'


class DoubleExtensionAttackTests(BaseTestCase):
    def test_exe_hidden_behind_pdf_extension_passes_allowlist(self) -> None:
        validator = FileValidator(
            allowed_extensions=frozenset({'pdf'}),
            blocked_extensions=frozenset(),
        )
        file = create_test_in_memory_uploaded_file()
        file.name = 'payload.exe.pdf'

        validator.validate(file)

    def test_bat_hidden_behind_txt_extension_passes_blocklist(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = 'script.bat.txt'

        validator.validate(file)

    def test_msi_hidden_behind_docx_passes_blocklist(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = 'installer.msi.docx'

        validator.validate(file)


@override_settings(STORAGES=STORAGES_OVERRIDE)
class XSSInFileMetadataTests(BaseTestCase):
    def test_script_tag_in_name_stored_raw(self) -> None:
        file = create_test_file(name='<script>alert(1)</script>')

        result = file.to_dict()

        assert '<script>' in result['name']

    def test_event_handler_in_name_stored_raw(self) -> None:
        file = create_test_file(name='" onmouseover="alert(1)"')

        result = file.to_dict()

        assert 'onmouseover' in result['name']

    def test_script_in_name_survives_to_json(self) -> None:
        file = create_test_file(name='<img src=x onerror=alert(1)>')

        parsed = json.loads(file.to_json())

        assert '<img' in parsed['name']


@override_settings(STORAGES=STORAGES_OVERRIDE)
class SizeBypassViaNoneTests(BaseTestCase):
    def test_none_size_rejected(self) -> None:
        validator = FileValidator(size_bytes_max=1)
        file = create_test_in_memory_uploaded_file(content=b'x' * 10_000)
        file.size = None

        with pytest.raises(FileValidationError, match='File size is unknown'):
            validator.validate(file)

    def test_none_size_rejected_by_factory(self) -> None:
        factory = FileFactory()
        file = create_test_in_memory_uploaded_file(content=b'x' * 500)
        file.size = None

        with pytest.raises(FileValidationError, match='File size is unknown'):
            factory.create(file)
