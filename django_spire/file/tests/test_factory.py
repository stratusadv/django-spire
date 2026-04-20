from __future__ import annotations

import pytest

from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.exceptions import FileValidationError
from django_spire.file.factory import (
    FileFactory,
    BATCH_SIZE_MAX,
    FILENAME_LENGTH_MAX,
    RELATED_FIELD_LENGTH_MAX
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


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileFactoryInitTests(BaseTestCase):
    def test_default_related_field(self) -> None:
        factory = FileFactory()

        assert factory.related_field == ''

    def test_default_app_name(self) -> None:
        factory = FileFactory()

        assert factory.app_name == 'Uncategorized'

    def test_related_field_exceeding_max_length_raises(self) -> None:
        with pytest.raises(ValueError, match='related_field must not exceed'):
            FileFactory(related_field='x' * (RELATED_FIELD_LENGTH_MAX + 1))

    def test_related_field_at_max_length(self) -> None:
        factory = FileFactory(related_field='x' * RELATED_FIELD_LENGTH_MAX)

        assert len(factory.related_field) == RELATED_FIELD_LENGTH_MAX


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileFactoryCreateTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = FileFactory()

    def test_create_returns_file(self) -> None:
        file = create_test_in_memory_uploaded_file()

        result = self.factory.create(file)

        assert isinstance(result, File)

    def test_create_saves_to_database(self) -> None:
        initial_count = File.objects.count()
        file = create_test_in_memory_uploaded_file()

        self.factory.create(file)

        assert File.objects.count() == initial_count + 1

    def test_create_sets_name(self) -> None:
        file = create_test_in_memory_uploaded_file(name='my_document')

        result = self.factory.create(file)

        assert result.name == 'my_document'

    def test_create_sets_type(self) -> None:
        file = create_test_in_memory_uploaded_file(file_type='png')

        result = self.factory.create(file)

        assert result.type == 'png'

    def test_create_sets_size_as_integer(self) -> None:
        content = b'x' * 500
        file = create_test_in_memory_uploaded_file(content=content)

        result = self.factory.create(file)

        assert result.size == 500

    def test_create_sets_related_field(self) -> None:
        factory = FileFactory(related_field='pfp')
        file = create_test_in_memory_uploaded_file()

        result = factory.create(file)

        assert result.related_field == 'pfp'


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileFactoryCreateManyTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = FileFactory()

    def test_create_many_returns_list(self) -> None:
        files = [
            create_test_in_memory_uploaded_file(name='file1'),
            create_test_in_memory_uploaded_file(name='file2'),
        ]

        result = self.factory.create_many(files)

        assert len(result) == 2

    def test_create_many_empty_list(self) -> None:
        result = self.factory.create_many([])

        assert result == []

    def test_create_many_exceeding_batch_size_raises(self) -> None:
        files = [
            create_test_in_memory_uploaded_file(name=f'file{i}')
            for i in range(BATCH_SIZE_MAX + 1)
        ]

        with pytest.raises(FileValidationError):
            self.factory.create_many(files)

    def test_create_many_at_exact_batch_size(self) -> None:
        files = [
            create_test_in_memory_uploaded_file(name=f'file{i}')
            for i in range(BATCH_SIZE_MAX)
        ]

        result = self.factory.create_many(files)

        assert len(result) == BATCH_SIZE_MAX

    def test_create_many_one_invalid_aborts_all(self) -> None:
        good = create_test_in_memory_uploaded_file(name='good')
        bad = create_test_in_memory_uploaded_file(name='bad', file_type='exe')
        initial_count = File.objects.count()

        with pytest.raises(FileValidationError):
            self.factory.create_many([good, bad])

        assert File.objects.count() == initial_count

    def test_create_many_duplicate_names(self) -> None:
        files = [
            create_test_in_memory_uploaded_file(name='same'),
            create_test_in_memory_uploaded_file(name='same'),
        ]

        result = self.factory.create_many(files)

        assert len(result) == 2
        assert result[0].name == result[1].name


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileFactoryDotfileTests(BaseTestCase):
    def test_dotfile_crashes_after_validation(self) -> None:
        factory = FileFactory()
        file = create_test_in_memory_uploaded_file()
        file.name = '.gitignore'

        with pytest.raises(ValueError, match='extension must not be empty'):
            factory.create(file)

    def test_file_with_trailing_dot_crashes_after_validation(self) -> None:
        factory = FileFactory()
        file = create_test_in_memory_uploaded_file()
        file.name = 'readme.'

        with pytest.raises(ValueError, match='extension must not be empty'):
            factory.create(file)


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileFactoryFilenameTruncationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = FileFactory()

    def test_name_at_max_length(self) -> None:
        name = 'a' * FILENAME_LENGTH_MAX
        file = create_test_in_memory_uploaded_file(name=name)

        result = self.factory.create(file)

        assert len(result.name) == FILENAME_LENGTH_MAX

    def test_name_exceeding_max_length_is_truncated(self) -> None:
        name = 'a' * (FILENAME_LENGTH_MAX + 50)
        file = create_test_in_memory_uploaded_file(name=name)

        result = self.factory.create(file)

        assert len(result.name) == FILENAME_LENGTH_MAX

    def test_truncation_preserves_prefix(self) -> None:
        name = 'important_' + 'a' * (FILENAME_LENGTH_MAX + 50)
        file = create_test_in_memory_uploaded_file(name=name)

        result = self.factory.create(file)

        assert result.name.startswith('important_')


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileFactoryNoneSizeTests(BaseTestCase):
    def test_none_size_defaults_to_zero(self) -> None:
        factory = FileFactory()
        file = create_test_in_memory_uploaded_file()
        file.size = None

        result = factory.create(file)

        assert result.size == 0
