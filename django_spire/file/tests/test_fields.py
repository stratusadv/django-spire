from __future__ import annotations

import json

from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.fields import MultipleFileField, SingleFileField
from django_spire.file.models import File
from django_spire.file.tests.factories import create_test_file
from django_spire.file.widgets import MultipleWidget, SingleFileWidget


STORAGES_OVERRIDE = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


@override_settings(STORAGES=STORAGES_OVERRIDE)
class MultipleFileFieldTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.field = MultipleFileField()

    def test_widget_is_multiple_widget(self):
        assert isinstance(self.field.widget, MultipleWidget)

    def test_prepare_value_with_files(self):
        file1 = create_test_file(name='file1')
        file2 = create_test_file(name='file2')

        result = self.field.prepare_value([file1, file2])
        parsed = json.loads(result)

        assert len(parsed) == 2

    def test_prepare_value_with_none(self):
        result = self.field.prepare_value(None)

        assert result == '[]'

    def test_prepare_value_with_empty_list(self):
        result = self.field.prepare_value([])

        assert result == '[]'

    def test_prepare_value_contains_file_data(self):
        file = create_test_file(name='test')

        result = self.field.prepare_value([file])
        parsed = json.loads(result)

        assert parsed[0]['name'] == 'test'
        assert 'id' in parsed[0]
        assert 'url' in parsed[0]

    def test_clean_returns_data(self):
        data = {'test': 'value'}

        result = self.field.clean(data)

        assert result == data


@override_settings(STORAGES=STORAGES_OVERRIDE)
class SingleFileFieldTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.field = SingleFileField()

    def test_widget_is_single_file_widget(self):
        assert isinstance(self.field.widget, SingleFileWidget)

    def test_prepare_value_with_file(self):
        file = create_test_file(name='test')

        result = self.field.prepare_value(file)
        parsed = json.loads(result)

        assert parsed['name'] == 'test'
        assert 'id' in parsed
        assert 'url' in parsed

    def test_prepare_value_with_none(self):
        result = self.field.prepare_value(None)

        assert result == 'null'

    def test_prepare_value_with_queryset(self):
        file = create_test_file(name='queryset_file')

        result = self.field.prepare_value(File.objects.filter(pk=file.pk))
        parsed = json.loads(result)

        assert parsed['name'] == 'queryset_file'

    def test_prepare_value_with_empty_queryset(self):
        result = self.field.prepare_value(File.objects.none())

        assert result == 'null'

    def test_clean_returns_data(self):
        data = {'test': 'value'}

        result = self.field.clean(data)

        assert result == data
