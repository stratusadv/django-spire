from __future__ import annotations

import json

from django.test import RequestFactory, override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.factory import RELATED_FIELD_LENGTH_MAX
from django_spire.file.models import File
from django_spire.file.tests.factories import create_test_in_memory_uploaded_file
from django_spire.file.views import file_upload_ajax_multiple, file_upload_ajax_single


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
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()

    def test_post_creates_files(self) -> None:
        initial_count = File.objects.count()
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        file_upload_ajax_multiple(request)

        assert File.objects.count() == initial_count + 1

    def test_post_returns_json_response(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'

    def test_post_returns_success_type(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert data['type'] == 'success'

    def test_post_returns_files_in_response(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file(name='test_upload')

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert 'files' in data
        assert len(data['files']) == 1
        assert data['files'][0]['name'] == 'test_upload'

    def test_get_returns_error_response(self) -> None:
        request = self.factory.get('/upload/multiple/ajax')
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileMultipleUploadAjaxEdgeCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()

    def test_post_no_files_creates_nothing(self) -> None:
        initial_count = File.objects.count()

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': ''},
        )
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert data['type'] == 'success'
        assert data['files'] == []
        assert File.objects.count() == initial_count

    def test_post_related_field_at_max_length(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': 'x' * RELATED_FIELD_LENGTH_MAX},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert data['type'] == 'success'

    def test_post_related_field_exceeding_max_length(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': 'x' * (RELATED_FIELD_LENGTH_MAX + 1)},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_post_missing_related_field_defaults_to_empty(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post('/upload/multiple/ajax')
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert data['type'] == 'success'

    def test_post_blocked_extension_returns_error(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file(name='malware', file_type='exe')

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_put_returns_error(self) -> None:
        request = self.factory.put('/upload/multiple/ajax')
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_delete_returns_error(self) -> None:
        request = self.factory.delete('/upload/multiple/ajax')
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_post_multiple_files(self) -> None:
        file1 = create_test_in_memory_uploaded_file(name='file1')
        file2 = create_test_in_memory_uploaded_file(name='file2')

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': ''},
        )
        request.FILES['file1'] = file1
        request.FILES['file2'] = file2
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert data['type'] == 'success'
        assert len(data['files']) == 2

    def test_post_related_field_with_path_traversal(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/multiple/ajax',
            data={'related_field': '../../etc'},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_multiple(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileSingleUploadAjaxViewTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()

    def test_post_creates_file(self) -> None:
        initial_count = File.objects.count()
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        file_upload_ajax_single(request)

        assert File.objects.count() == initial_count + 1

    def test_post_returns_json_response(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_single(request)

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'

    def test_post_returns_success_type(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'success'

    def test_post_returns_file_in_response(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file(name='single_upload')

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert 'file' in data
        assert data['file']['name'] == 'single_upload'

    def test_get_returns_error_response(self) -> None:
        request = self.factory.get('/upload/single/ajax')
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileSingleUploadAjaxEdgeCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()

    def test_post_no_file_returns_error(self) -> None:
        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': ''},
        )
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_post_related_field_exceeding_max_length(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': 'x' * (RELATED_FIELD_LENGTH_MAX + 1)},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_post_blocked_extension_returns_error(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file(name='malware', file_type='exe')

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': ''},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_post_multiple_files_uses_first(self) -> None:
        file1 = create_test_in_memory_uploaded_file(name='first')
        file2 = create_test_in_memory_uploaded_file(name='second')

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': ''},
        )
        request.FILES['file1'] = file1
        request.FILES['file2'] = file2
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'success'

    def test_put_returns_error(self) -> None:
        request = self.factory.put('/upload/single/ajax')
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'

    def test_post_missing_related_field_defaults_to_empty(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post('/upload/single/ajax')
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'success'

    def test_post_related_field_with_path_traversal(self) -> None:
        uploaded_file = create_test_in_memory_uploaded_file()

        request = self.factory.post(
            '/upload/single/ajax',
            data={'related_field': '../../../etc'},
        )
        request.FILES['file'] = uploaded_file
        request.user = self.super_user

        response = file_upload_ajax_single(request)
        data = json.loads(response.content)

        assert data['type'] == 'error'
