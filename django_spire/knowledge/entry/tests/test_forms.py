from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from django.test import RequestFactory
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection
from django_spire.knowledge.entry.forms import EntryFilesForm
from django_spire.knowledge.entry.models import Entry

if TYPE_CHECKING:
    from django.http import HttpRequest


class EntryFilesFormTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection = create_test_collection()
        self.factory = RequestFactory()

    def _build_request(self, uploaded_files: list[UploadedFile]) -> HttpRequest:
        request = self.factory.post('/', data={'import_files': uploaded_files})
        request.user = self.super_user
        return request

    def test_save_model_obj_creates_entries_from_uploaded_files(self):
        uploaded = [
            SimpleUploadedFile('test.txt', b'hello world', content_type='text/plain'),
            SimpleUploadedFile('test.md', b'# Title', content_type='text/markdown'),
        ]
        request = self._build_request(uploaded)

        form = EntryFilesForm(
            data={'import_files': uploaded, 'collection_pk': str(self.collection.pk)},
            files=MultiValueDict({'import_files.value': uploaded}),
        )
        response = form.save_model_obj(request)

        assert response.status == 200
        assert response.result == {
            'redirect': {
                'url': reverse(
                    'django_spire:knowledge:entry:template:file_list',
                    kwargs={'collection_pk': self.collection.pk},
                )
            }
        }

        entries = Entry.objects.filter(collection=self.collection)
        assert entries.count() == 2
        assert all(entry.name == 'test' for entry in entries)

    def test_save_model_obj_no_files_returns_error(self):
        request = self._build_request([])

        form = EntryFilesForm(
            data={'collection_pk': str(self.collection.pk)},
            files=MultiValueDict({'import_files.value': []}),
        )
        response = form.save_model_obj(request)

        assert response.status == 200
        assert response.result is None
        assert len(response.messages) == 1
        assert 'No files selected' in response.messages[0].message

        assert Entry.objects.filter(collection=self.collection).count() == 0
