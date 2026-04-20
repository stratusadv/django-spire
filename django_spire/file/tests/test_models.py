from __future__ import annotations

import json

from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.tests.factories import create_test_file


STORAGES_OVERRIDE = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileModelTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.file = create_test_file()

    def test_str(self) -> None:
        assert str(self.file) == self.file.name

    def test_default_is_active(self) -> None:
        assert self.file.is_active is True

    def test_default_is_deleted(self) -> None:
        assert self.file.is_deleted is False

    def test_name_field(self) -> None:
        assert self.file.name == 'test_file'

    def test_type_field(self) -> None:
        assert self.file.type == 'pdf'

    def test_size_field(self) -> None:
        assert self.file.size == 1_048_576

    def test_formatted_size(self) -> None:
        assert self.file.formatted_size == '1.0 MB'

    def test_formatted_size_zero(self) -> None:
        file = create_test_file(size=0)

        assert file.formatted_size == '0 KB'

    def test_related_field_default(self) -> None:
        assert self.file.related_field == ''

    def test_related_field_set(self) -> None:
        file = create_test_file(related_field='abc')

        assert file.related_field == 'abc'

    def test_content_type_null(self) -> None:
        assert self.file.content_type is None

    def test_object_id_null(self) -> None:
        assert self.file.object_id is None

    def test_created_datetime_auto_set(self) -> None:
        assert self.file.created_datetime is not None

    def test_to_dict(self) -> None:
        result = self.file.to_dict()

        assert result['name'] == self.file.name
        assert result['id'] == self.file.id
        assert 'url' in result

    def test_to_dict_keys(self) -> None:
        result = self.file.to_dict()

        assert set(result.keys()) == {'name', 'url', 'id'}

    def test_to_json(self) -> None:
        result = self.file.to_json()
        parsed = json.loads(result)

        assert parsed['name'] == self.file.name
        assert parsed['id'] == self.file.id

    def test_file_field_url(self) -> None:
        assert self.file.file.url is not None


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileModelEdgeCaseTests(BaseTestCase):
    def test_str_empty_name(self) -> None:
        file = create_test_file(name='')

        assert str(file) == ''

    def test_formatted_size_one_byte(self) -> None:
        file = create_test_file(size=1)

        assert file.formatted_size == '0.0 KB'

    def test_formatted_size_just_under_mb(self) -> None:
        file = create_test_file(size=1_048_575)

        assert 'KB' in file.formatted_size

    def test_formatted_size_exact_gb(self) -> None:
        file = create_test_file(size=1_073_741_824)

        assert file.formatted_size == '1.0 GB'

    def test_formatted_size_exact_tb(self) -> None:
        file = create_test_file(size=1_099_511_627_776)

        assert file.formatted_size == '1.0 TB'

    def test_to_dict_returns_correct_id_type(self) -> None:
        file = create_test_file()
        result = file.to_dict()

        assert isinstance(result['id'], int)

    def test_to_json_is_valid_json(self) -> None:
        file = create_test_file()
        result = file.to_json()

        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_to_json_roundtrips_to_dict(self) -> None:
        file = create_test_file()

        assert json.loads(file.to_json()) == file.to_dict()

    def test_unicode_name(self) -> None:
        file = create_test_file(name='документ')

        assert str(file) == 'документ'
        assert file.to_dict()['name'] == 'документ'

    def test_special_characters_in_name(self) -> None:
        file = create_test_file(name='file <script>alert(1)</script>')

        result = file.to_dict()

        assert result['name'] == 'file <script>alert(1)</script>'
