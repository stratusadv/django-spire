from __future__ import annotations

from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.admin import FileAdmin
from django_spire.file.models import File
from django_spire.file.tests.factories import create_test_file
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket


STORAGES_OVERRIDE = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileAdminTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.site = AdminSite()
        self.admin = FileAdmin(File, self.site)
        self.file = create_test_file()

    def test_list_display(self):
        expected = ('id', 'name', 'type', 'size', 'content_object_link', 'file_link')

        assert self.admin.list_display == expected

    def test_list_filter(self):
        assert self.admin.list_filter == ('type',)

    def test_search_fields(self):
        assert self.admin.search_fields == ('id', 'name', 'type')

    def test_ordering(self):
        assert self.admin.ordering == ('-id',)

    def test_content_object_link_no_related_object(self):
        result = self.admin.content_object_link(self.file)

        assert result == 'No Related Object'

    def test_content_object_link_with_related_object(self):
        ticket = create_test_helpdesk_ticket()
        content_type = ContentType.objects.get_for_model(ticket.__class__)
        self.file.content_type = content_type
        self.file.object_id = ticket.pk
        self.file.save()

        result = self.admin.content_object_link(self.file)

        assert 'href=' in result
        assert str(ticket) in result

    def test_file_link(self):
        result = self.admin.file_link(self.file)

        assert f'href="{self.file.file.url}"' in result
        assert self.file.name in result
        assert 'download' in result
