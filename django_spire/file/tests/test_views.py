from __future__ import annotations

import json

from django.test import RequestFactory, override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.models import File
from django_spire.file.tests.factories import create_test_in_memory_uploaded_file
from django_spire.file.views import file_multiple_upload_ajax, file_single_upload_ajax


STORAGES_OVERRIDE = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileMultipleUploadAjaxViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.factory = RequestFactory()

    def test_post_creates_files(self):
        initial_count = File.objects.count()
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        file_multiple_upload_ajax(request)

        assert File.objects.count() == initial_count + 1

    def test_post_returns_json_response(self):
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_multiple_upload_ajax(request)

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'

    def test_post_returns_files_in_response(self):
        uploaded_file = create_test_in_memory_uploaded_file(name='test_upload')

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_multiple_upload_ajax(request)
        data = json.loads(response.content)

        assert 'files' in data
        assert len(data['files']) == 1
        assert data['files'][0]['name'] == 'test_upload'

    def test_get_returns_none(self):
        request = self.factory.get('/upload/multiple/ajax')
        request.user = self.super_user

        response = file_multiple_upload_ajax(request)

        assert response is None


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileSingleUploadAjaxViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.factory = RequestFactory()

    def test_post_creates_file(self):
        initial_count = File.objects.count()
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        file_single_upload_ajax(request)

        assert File.objects.count() == initial_count + 1

    def test_post_returns_json_response(self):
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_single_upload_ajax(request)

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'

    def test_post_returns_file_in_response(self):
        uploaded_file = create_test_in_memory_uploaded_file(name='single_upload')

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_single_upload_ajax(request)
        data = json.loads(response.content)

        assert 'file' in data
        assert data['file']['name'] == 'single_upload'

    def test_get_returns_none(self):
        request = self.factory.get('/upload/single/ajax')
        request.user = self.super_user

        response = file_single_upload_ajax(request)

        assert response is None
