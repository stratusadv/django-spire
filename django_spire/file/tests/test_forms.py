from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.fields import MultipleFileField
from django_spire.file.forms import FileForm


class FileFormTests(BaseTestCase):
    def test_has_files_field(self):
        assert 'files' in FileForm().fields

    def test_files_field_is_multiple_file_field(self):
        form = FileForm()

        assert isinstance(form.fields['files'], MultipleFileField)

    def test_form_field_count(self):
        form = FileForm()

        assert len(form.fields) == 1
