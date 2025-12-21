from __future__ import annotations

from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.models import File
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
class FileQuerySetTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.file1 = create_test_file(name='File 1')
        self.file2 = create_test_file(name='File 2')

    def test_active_returns_non_deleted(self):
        result = File.objects.active()

        assert self.file1 in result
        assert self.file2 in result

    def test_active_excludes_deleted(self):
        self.file1.is_deleted = True
        self.file1.save()

        result = File.objects.active()

        assert self.file1 not in result
        assert self.file2 in result

    def test_active_excludes_inactive(self):
        self.file1.is_active = False
        self.file1.save()

        result = File.objects.active()

        assert self.file1 not in result
        assert self.file2 in result

    def test_active_excludes_deleted_and_inactive(self):
        self.file1.is_deleted = True
        self.file1.is_active = False
        self.file1.save()

        result = File.objects.active()

        assert self.file1 not in result
        assert self.file2 in result

    def test_related_field_filters_correctly(self):
        self.file1.related_field = 'abc'
        self.file1.save()
        self.file2.related_field = 'xyz'
        self.file2.save()

        result = File.objects.related_field('abc')

        assert self.file1 in result
        assert self.file2 not in result

    def test_related_field_returns_empty_when_no_match(self):
        self.file1.related_field = 'abc'
        self.file1.save()

        result = File.objects.related_field('xyz')

        assert result.count() == 0

    def test_related_field_filters_null_values(self):
        self.file1.related_field = None
        self.file1.save()
        self.file2.related_field = 'abc'
        self.file2.save()

        result = File.objects.related_field(None)

        assert self.file1 in result
        assert self.file2 not in result

    def test_chaining_active_and_related_field(self):
        self.file1.related_field = 'abc'
        self.file1.save()
        self.file2.related_field = 'abc'
        self.file2.is_deleted = True
        self.file2.save()

        result = File.objects.active().related_field('abc')

        assert self.file1 in result
        assert self.file2 not in result
