from __future__ import annotations

import pytest

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.path import FilePathBuilder


class FilePathBuilderInitTests(BaseTestCase):
    def test_empty_base_folder_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match='base_folder must not be empty'):
            FilePathBuilder(base_folder='')

    def test_valid_base_folder(self) -> None:
        builder = FilePathBuilder(base_folder='uploads')

        assert builder.base_folder == 'uploads'

    def test_default_app_name(self) -> None:
        builder = FilePathBuilder(base_folder='uploads')

        assert builder.app_name == 'Uncategorized'

    def test_whitespace_only_base_folder_does_not_raise(self) -> None:
        builder = FilePathBuilder(base_folder='   ')

        assert builder.base_folder == '   '


class FilePathBuilderBuildTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.builder = FilePathBuilder(base_folder='uploads', app_name='TestApp')

    def test_path_starts_with_base_folder(self) -> None:
        path = self.builder.build('document', 'pdf')

        assert path.startswith('uploads/')

    def test_path_contains_app_name(self) -> None:
        path = self.builder.build('document', 'pdf')

        assert '/TestApp/' in path

    def test_path_ends_with_filename(self) -> None:
        path = self.builder.build('document', 'pdf')

        assert path.endswith('document.pdf')

    def test_path_contains_related_field(self) -> None:
        path = self.builder.build('document', 'pdf', related_field='pfp')

        assert '/pfp/' in path

    def test_path_without_related_field(self) -> None:
        path = self.builder.build('document', 'pdf')

        assert path.count('/') == 2

    def test_path_with_related_field(self) -> None:
        path = self.builder.build('document', 'pdf', related_field='pfp')

        assert path.count('/') == 3

    def test_path_contains_random_token(self) -> None:
        path_one = self.builder.build('document', 'pdf')
        path_two = self.builder.build('document', 'pdf')

        assert path_one != path_two

    def test_token_is_filename_prefix(self) -> None:
        path = self.builder.build('document', 'pdf')
        filename = path.rsplit('/', 1)[1]

        assert '_document.pdf' in filename

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match='name must not be empty'):
            self.builder.build('', 'pdf')

    def test_empty_extension_raises(self) -> None:
        with pytest.raises(ValueError, match='extension must not be empty'):
            self.builder.build('document', '')


class FilePathBuilderPathTraversalTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.builder = FilePathBuilder(base_folder='uploads', app_name='TestApp')

    def test_name_with_path_traversal(self) -> None:
        path = self.builder.build('../../etc/passwd', 'txt')

        assert '/..' in path

    def test_name_with_forward_slash(self) -> None:
        path = self.builder.build('sub/dir/file', 'txt')

        assert 'sub/dir/file' in path

    def test_name_with_backslash(self) -> None:
        path = self.builder.build('sub\\dir\\file', 'txt')

        assert 'sub\\dir\\file' in path

    def test_name_with_null_byte(self) -> None:
        path = self.builder.build('file\x00evil', 'txt')

        assert '\x00' in path

    def test_app_name_with_slashes(self) -> None:
        builder = FilePathBuilder(base_folder='uploads', app_name='../../etc')
        path = builder.build('file', 'txt')

        assert '../../etc' in path

    def test_related_field_with_path_traversal(self) -> None:
        path = self.builder.build('file', 'txt', related_field='../../etc')

        assert '../../etc' in path


class FilePathBuilderUnicodeTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.builder = FilePathBuilder(base_folder='uploads')

    def test_unicode_name(self) -> None:
        path = self.builder.build('документ', 'pdf')

        assert path.endswith('документ.pdf')

    def test_unicode_app_name(self) -> None:
        builder = FilePathBuilder(base_folder='uploads', app_name='応用')
        path = builder.build('file', 'pdf')

        assert '/応用/' in path
