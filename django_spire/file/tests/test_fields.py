from __future__ import annotations

import json

from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.fields import MultipleFileField, SingleFileField
from django_spire.file.models import File
from django_spire.file.tests.factories import create_test_file
from django_spire.file.widgets import MultipleFileWidget, SingleFileWidget


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
    def setUp(self) -> None:
        super().setUp()

        self.field = MultipleFileField()

    def test_widget_is_multiple_file_widget(self) -> None:
        assert isinstance(self.field.widget, MultipleFileWidget)

    def test_prepare_value_with_files(self) -> None:
        file1 = create_test_file(name='file1')
        file2 = create_test_file(name='file2')

        result = self.field.prepare_value([file1, file2])
        parsed = json.loads(result)

        assert len(parsed) == 2

    def test_prepare_value_with_none(self) -> None:
        result = self.field.prepare_value(None)

        assert result == '[]'

    def test_prepare_value_with_empty_list(self) -> None:
        result = self.field.prepare_value([])

        assert result == '[]'

    def test_prepare_value_contains_file_data(self) -> None:
        file = create_test_file(name='test')

        result = self.field.prepare_value([file])
        parsed = json.loads(result)

        assert parsed[0]['name'] == 'test'
        assert 'id' in parsed[0]
        assert 'url' in parsed[0]

    def test_clean_returns_data(self) -> None:
        data = {'test': 'value'}

        result = self.field.clean(data)

        assert result == data


@override_settings(STORAGES=STORAGES_OVERRIDE)
class MultipleFileFieldEdgeCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.field = MultipleFileField()

    def test_default_related_field(self) -> None:
        assert self.field.related_field == ''

    def test_custom_related_field(self) -> None:
        field = MultipleFileField(related_field='pfp')

        assert field.related_field == 'pfp'

    def test_prepare_value_large_list(self) -> None:
        files = [create_test_file(name=f'file{i}') for i in range(20)]

        result = self.field.prepare_value(files)
        parsed = json.loads(result)

        assert len(parsed) == 20

    def test_prepare_value_output_is_valid_json(self) -> None:
        file = create_test_file()

        result = self.field.prepare_value([file])

        json.loads(result)

    def test_clean_returns_none(self) -> None:
        result = self.field.clean(None)

        assert result is None

    def test_clean_returns_empty_list(self) -> None:
        result = self.field.clean([])

        assert result == []

    def test_clean_returns_list_of_dicts(self) -> None:
        data = [{'id': 1}, {'id': 2}]

        result = self.field.clean(data)

        assert result == data


@override_settings(STORAGES=STORAGES_OVERRIDE)
class SingleFileFieldTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.field = SingleFileField()

    def test_widget_is_single_file_widget(self) -> None:
        assert isinstance(self.field.widget, SingleFileWidget)

    def test_prepare_value_with_file(self) -> None:
        file = create_test_file(name='test')

        result = self.field.prepare_value(file)
        parsed = json.loads(result)

        assert parsed['name'] == 'test'
        assert 'id' in parsed
        assert 'url' in parsed

    def test_prepare_value_with_none(self) -> None:
        result = self.field.prepare_value(None)

        assert result == 'null'

    def test_prepare_value_with_queryset(self) -> None:
        file = create_test_file(name='queryset_file')

        result = self.field.prepare_value(File.objects.filter(pk=file.pk))
        parsed = json.loads(result)

        assert parsed['name'] == 'queryset_file'

    def test_prepare_value_with_empty_queryset(self) -> None:
        result = self.field.prepare_value(File.objects.none())

        assert result == 'null'

    def test_clean_returns_data(self) -> None:
        data = {'test': 'value'}

        result = self.field.clean(data)

        assert result == data


@override_settings(STORAGES=STORAGES_OVERRIDE)
class SingleFileFieldEdgeCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.field = SingleFileField()

    def test_default_related_field(self) -> None:
        assert self.field.related_field == ''

    def test_custom_related_field(self) -> None:
        field = SingleFileField(related_field='pfp')

        assert field.related_field == 'pfp'

    def test_prepare_value_output_is_valid_json(self) -> None:
        file = create_test_file()

        result = self.field.prepare_value(file)

        json.loads(result)

    def test_prepare_value_queryset_with_multiple_results_uses_first(self) -> None:
        file1 = create_test_file(name='first')
        file2 = create_test_file(name='second')

        result = self.field.prepare_value(
            File.objects.filter(pk__in=[file1.pk, file2.pk]).order_by('pk')
        )
        parsed = json.loads(result)

        assert parsed['name'] == 'first'

    def test_clean_returns_none(self) -> None:
        result = self.field.clean(None)

        assert result is None

    def test_clean_returns_dict(self) -> None:
        data = {'id': 1, 'name': 'test'}

        result = self.field.clean(data)

        assert result == data
