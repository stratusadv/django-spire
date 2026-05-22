from __future__ import annotations

import json

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.widgets import MultipleFileWidget, SingleFileWidget


class MultipleFileWidgetTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.widget = MultipleFileWidget()

    def test_needs_multipart_form(self) -> None:
        assert self.widget.needs_multipart_form is True

    def test_template_name(self) -> None:
        assert self.widget.template_name == 'django_spire/file/widget/multiple_file_widget.html'

    def test_value_from_datadict(self) -> None:
        data = {
            'files_data': json.dumps([{'id': 1, 'name': 'test'}])
        }

        result = self.widget.value_from_datadict(data, None, 'files')

        assert result == [{'id': 1, 'name': 'test'}]

    def test_value_from_datadict_empty(self) -> None:
        data = {
            'files_data': json.dumps([])
        }

        result = self.widget.value_from_datadict(data, None, 'files')

        assert result == []

    def test_value_from_datadict_multiple_files(self) -> None:
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


class MultipleFileWidgetEdgeCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.widget = MultipleFileWidget()

    def test_value_from_datadict_malformed_json(self) -> None:
        data = {'files_data': '{not valid json'}

        result = self.widget.value_from_datadict(data, None, 'files')

        assert result == []

    def test_value_from_datadict_json_string_instead_of_list(self) -> None:
        data = {'files_data': json.dumps('not a list')}

        result = self.widget.value_from_datadict(data, None, 'files')

        assert result == 'not a list'

    def test_value_from_datadict_json_dict_instead_of_list(self) -> None:
        data = {'files_data': json.dumps({'id': 1})}

        result = self.widget.value_from_datadict(data, None, 'files')

        assert result == {'id': 1}

    def test_value_from_datadict_json_null(self) -> None:
        data = {'files_data': json.dumps(None)}

        result = self.widget.value_from_datadict(data, None, 'files')

        assert result is None

    def test_value_from_datadict_json_integer(self) -> None:
        data = {'files_data': json.dumps(42)}

        result = self.widget.value_from_datadict(data, None, 'files')

        assert result == 42

    def test_value_from_datadict_no_data_no_files(self) -> None:
        result = self.widget.value_from_datadict({}, None, 'files')

        assert result == []

    def test_value_from_datadict_empty_string_json(self) -> None:
        data = {'files_data': ''}

        result = self.widget.value_from_datadict(data, None, 'files')

        assert result == []

    def test_value_from_datadict_nested_malicious_structure(self) -> None:
        payload = [{'id': 1, '__class__': 'File', 'is_active': False}]
        data = {'files_data': json.dumps(payload)}

        result = self.widget.value_from_datadict(data, None, 'files')

        assert result == payload


class SingleFileWidgetTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.widget = SingleFileWidget()

    def test_needs_multipart_form(self) -> None:
        assert self.widget.needs_multipart_form is True

    def test_template_name(self) -> None:
        assert self.widget.template_name == 'django_spire/file/widget/single_file_widget.html'

    def test_value_from_datadict(self) -> None:
        data = {
            'file_data': json.dumps({'id': 1, 'name': 'test'})
        }

        result = self.widget.value_from_datadict(data, None, 'file')

        assert result == {'id': 1, 'name': 'test'}

    def test_value_from_datadict_null(self) -> None:
        data = {
            'file_data': json.dumps(None)
        }

        result = self.widget.value_from_datadict(data, None, 'file')

        assert result is None


class SingleFileWidgetEdgeCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.widget = SingleFileWidget()

    def test_value_from_datadict_malformed_json(self) -> None:
        data = {'file_data': '{not valid'}

        result = self.widget.value_from_datadict(data, None, 'file')

        assert result is None

    def test_value_from_datadict_json_list_instead_of_dict(self) -> None:
        data = {'file_data': json.dumps([1, 2, 3])}

        result = self.widget.value_from_datadict(data, None, 'file')

        assert result == [1, 2, 3]

    def test_value_from_datadict_json_string(self) -> None:
        data = {'file_data': json.dumps('just a string')}

        result = self.widget.value_from_datadict(data, None, 'file')

        assert result == 'just a string'

    def test_value_from_datadict_json_integer(self) -> None:
        data = {'file_data': json.dumps(42)}

        result = self.widget.value_from_datadict(data, None, 'file')

        assert result == 42

    def test_value_from_datadict_no_data_no_files(self) -> None:
        result = self.widget.value_from_datadict({}, None, 'file')

        assert result is None

    def test_value_from_datadict_empty_string_json(self) -> None:
        data = {'file_data': ''}

        result = self.widget.value_from_datadict(data, None, 'file')

        assert result is None

    def test_value_from_datadict_nested_malicious_structure(self) -> None:
        payload = {'id': 1, '__class__': 'File', 'is_deleted': True}
        data = {'file_data': json.dumps(payload)}

        result = self.widget.value_from_datadict(data, None, 'file')

        assert result == payload

    def test_value_from_datadict_deeply_nested_json(self) -> None:
        payload = {'id': 1, 'nested': {'a': {'b': {'c': 'd'}}}}
        data = {'file_data': json.dumps(payload)}

        result = self.widget.value_from_datadict(data, None, 'file')

        assert result == payload
