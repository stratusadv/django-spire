from __future__ import annotations

import json

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.widgets import MultipleWidget, SingleFileWidget


class MultipleWidgetTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.widget = MultipleWidget()

    def test_needs_multipart_form(self):
        assert self.widget.needs_multipart_form is True

    def test_template_name(self):
        assert self.widget.template_name == 'django_spire/file/widget/multiple_file_widget.html'

    def test_value_from_datadict(self):
        data = {
            'files_data': json.dumps([{'id': 1, 'name': 'test'}])
        }

        result = self.widget.value_from_datadict(data, None, 'files')

        assert result == [{'id': 1, 'name': 'test'}]

    def test_value_from_datadict_empty(self):
        data = {
            'files_data': json.dumps([])
        }

        result = self.widget.value_from_datadict(data, None, 'files')

        assert result == []

    def test_value_from_datadict_multiple_files(self):
        data = {
            'files_data': json.dumps([
                {'id': 1, 'name': 'file1'},
                {'id': 2, 'name': 'file2'},
            ])
        }

        result = self.widget.value_from_datadict(data, None, 'files')

        assert len(result) == 2
        assert result[0]['name'] == 'file1'
        assert result[1]['name'] == 'file2'


class SingleFileWidgetTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.widget = SingleFileWidget()

    def test_needs_multipart_form(self):
        assert self.widget.needs_multipart_form is True

    def test_template_name(self):
        assert self.widget.template_name == 'django_spire/file/widget/single_file_widget.html'

    def test_value_from_datadict(self):
        data = {
            'file_data': json.dumps({'id': 1, 'name': 'test'})
        }

        result = self.widget.value_from_datadict(data, None, 'file')

        assert result == {'id': 1, 'name': 'test'}

    def test_value_from_datadict_null(self):
        data = {
            'file_data': json.dumps(None)
        }

        result = self.widget.value_from_datadict(data, None, 'file')

        assert result is None
