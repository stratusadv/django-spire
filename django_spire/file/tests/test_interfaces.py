from __future__ import annotations

from django.conf import settings
from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.interfaces import (
    FileFormatter,
    MultiFileUploader,
    SingleFileUploader,
)
from django_spire.file.models import File
from django_spire.file.tests.factories import create_test_in_memory_uploaded_file


STORAGES_OVERRIDE = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


class FileFormatterTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.uploaded_file = create_test_in_memory_uploaded_file(
            name='document',
            file_type='pdf',
            content=b'test content',
        )
        self.formatter = FileFormatter(file=self.uploaded_file)

    def test_format_name(self):
        assert self.formatter.name == 'document'

    def test_parse_type(self):
        assert self.formatter.type == 'pdf'

    def test_location_contains_base_folder(self):
        assert self.formatter.location.startswith(settings.BASE_FOLDER_NAME + '/')

    def test_location_contains_app_name(self):
        assert '/Uncategorized/' in self.formatter.location

    def test_location_contains_file_name(self):
        assert self.formatter.location.endswith('document')

    def test_location_with_related_field(self):
        formatter = FileFormatter(
            file=self.uploaded_file,
            related_field='abc',
        )

        assert '/abc/' in formatter.location

    def test_location_with_custom_app_name(self):
        formatter = FileFormatter(
            file=self.uploaded_file,
            app_name='CustomApp',
        )

        assert '/CustomApp/' in formatter.location

    def test_size_verbose_kb(self):
        content = b'x' * 1000
        uploaded_file = create_test_in_memory_uploaded_file(content=content)
        formatter = FileFormatter(file=uploaded_file)

        assert 'kb' in formatter.size_verbose()

    def test_size_verbose_mb(self):
        content = b'x' * 1000000
        uploaded_file = create_test_in_memory_uploaded_file(content=content)
        formatter = FileFormatter(file=uploaded_file)

        assert 'Mb' in formatter.size_verbose()

    @override_settings(STORAGES=STORAGES_OVERRIDE)
    def test_null_file_obj_returns_file(self):
        result = self.formatter.null_file_obj()

        assert isinstance(result, File)
        assert result.name == 'document'
        assert result.type == 'pdf'

    @override_settings(STORAGES=STORAGES_OVERRIDE)
    def test_null_file_obj_not_saved(self):
        result = self.formatter.null_file_obj()

        assert result.pk is None


@override_settings(STORAGES=STORAGES_OVERRIDE)
class SingleFileUploaderTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.uploader = SingleFileUploader(related_field='abc')
        self.uploaded_file = create_test_in_memory_uploaded_file()

    def test_upload_creates_file(self):
        initial_count = File.objects.count()

        self.uploader.upload(self.uploaded_file)

        assert File.objects.count() == initial_count + 1

    def test_upload_returns_file(self):
        result = self.uploader.upload(self.uploaded_file)

        assert isinstance(result, File)
        assert result.pk is not None

    def test_upload_sets_name(self):
        result = self.uploader.upload(self.uploaded_file)

        assert result.name == 'test_file'

    def test_upload_sets_type(self):
        result = self.uploader.upload(self.uploaded_file)

        assert result.type == 'pdf'

    def test_null_file_obj(self):
        result = self.uploader.null_file_obj(self.uploaded_file)

        assert isinstance(result, File)
        assert result.pk is None


@override_settings(STORAGES=STORAGES_OVERRIDE)
class MultiFileUploaderTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.uploader = MultiFileUploader(related_field='abc')
        self.uploaded_files = [
            create_test_in_memory_uploaded_file(name='file1'),
            create_test_in_memory_uploaded_file(name='file2'),
        ]

    def test_upload_creates_multiple_files(self):
        initial_count = File.objects.count()

        self.uploader.upload(self.uploaded_files)

        assert File.objects.count() == initial_count + 2

    def test_upload_returns_list_of_files(self):
        result = self.uploader.upload(self.uploaded_files)

        assert isinstance(result, list)
        assert len(result) == 2

    def test_upload_returns_file_instances(self):
        result = self.uploader.upload(self.uploaded_files)

        for file in result:
            assert isinstance(file, File)
            assert file.pk is not None

    def test_upload_sets_names(self):
        result = self.uploader.upload(self.uploaded_files)
        names = [f.name for f in result]

        assert 'file1' in names
        assert 'file2' in names

    def test_upload_empty_list(self):
        result = self.uploader.upload([])

        assert result == []

    def test_null_file_obj(self):
        uploaded_file = create_test_in_memory_uploaded_file()
        result = self.uploader.null_file_obj(uploaded_file)

        assert isinstance(result, File)
        assert result.pk is None
