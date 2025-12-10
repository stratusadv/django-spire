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
    def setUp(self):
        super().setUp()

        self.file = create_test_file()

    def test_str(self):
        assert str(self.file) == self.file.name

    def test_default_is_active(self):
        assert self.file.is_active is True

    def test_default_is_deleted(self):
        assert self.file.is_deleted is False

    def test_name_field(self):
        assert self.file.name == 'test_file'

    def test_type_field(self):
        assert self.file.type == 'pdf'

    def test_size_field(self):
        assert self.file.size == '1.5 Mb'

    def test_related_field_default(self):
        assert self.file.related_field is None

    def test_related_field_set(self):
        file = create_test_file(related_field='abc')
        assert file.related_field == 'abc'

    def test_content_type_null(self):
        assert self.file.content_type is None

    def test_object_id_null(self):
        assert self.file.object_id is None

    def test_created_datetime_auto_set(self):
        assert self.file.created_datetime is not None

    def test_to_dict(self):
        result = self.file.to_dict()

        assert result['name'] == self.file.name
        assert result['id'] == self.file.id
        assert 'url' in result

    def test_to_dict_keys(self):
        result = self.file.to_dict()

        assert set(result.keys()) == {'name', 'url', 'id'}

    def test_to_json(self):
        result = self.file.to_json()
        parsed = json.loads(result)

        assert parsed['name'] == self.file.name
        assert parsed['id'] == self.file.id

    def test_file_field_url(self):
        assert self.file.file.url is not None
