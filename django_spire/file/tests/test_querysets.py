from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from django_spire.core.tests.test_cases import BaseTestCase
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
class FileQuerySetTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.file1 = create_test_file(name='File 1')
        self.file2 = create_test_file(name='File 2')

    def test_active_returns_non_deleted(self) -> None:
        result = File.objects.active()

        assert self.file1 in result
        assert self.file2 in result

    def test_active_excludes_deleted(self) -> None:
        self.file1.is_deleted = True
        self.file1.save()

        result = File.objects.active()

        assert self.file1 not in result
        assert self.file2 in result

    def test_active_excludes_inactive(self) -> None:
        self.file1.is_active = False
        self.file1.save()

        result = File.objects.active()

        assert self.file1 not in result
        assert self.file2 in result

    def test_active_excludes_deleted_and_inactive(self) -> None:
        self.file1.is_deleted = True
        self.file1.is_active = False
        self.file1.save()

        result = File.objects.active()

        assert self.file1 not in result
        assert self.file2 in result

    def test_related_field_filters_correctly(self) -> None:
        self.file1.related_field = 'abc'
        self.file1.save()
        self.file2.related_field = 'xyz'
        self.file2.save()

        result = File.objects.related_field('abc')

        assert self.file1 in result
        assert self.file2 not in result

    def test_related_field_returns_empty_when_no_match(self) -> None:
        self.file1.related_field = 'abc'
        self.file1.save()

        result = File.objects.related_field('xyz')

        assert result.count() == 0

    def test_related_field_filters_empty_values(self) -> None:
        self.file1.related_field = ''
        self.file1.save()
        self.file2.related_field = 'abc'
        self.file2.save()

        result = File.objects.related_field('')

        assert self.file1 in result
        assert self.file2 not in result

    def test_chaining_active_and_related_field(self) -> None:
        self.file1.related_field = 'abc'
        self.file1.save()
        self.file2.related_field = 'abc'
        self.file2.is_deleted = True
        self.file2.save()

        result = File.objects.active().related_field('abc')

        assert self.file1 in result
        assert self.file2 not in result


@override_settings(STORAGES=STORAGES_OVERRIDE)
class FileQuerySetEdgeCaseTests(BaseTestCase):
    def test_active_on_empty_table(self) -> None:
        File.objects.all().delete()

        result = File.objects.active()

        assert result.count() == 0

    def test_active_inactive_but_not_deleted(self) -> None:
        file = create_test_file(is_active=False, is_deleted=False)

        result = File.objects.active()

        assert file not in result

    def test_active_deleted_but_still_active_flag(self) -> None:
        file = create_test_file(is_active=True, is_deleted=True)

        result = File.objects.active()

        assert file not in result

    def test_related_field_does_not_do_partial_match(self) -> None:
        file = create_test_file(related_field='abcdef')

        result = File.objects.related_field('abc')

        assert file not in result

    def test_related_field_is_case_sensitive(self) -> None:
        file = create_test_file(related_field='ABC')

        result = File.objects.related_field('abc')

        assert file not in result

    def test_chaining_related_field_twice(self) -> None:
        file = create_test_file(related_field='abc')

        result = File.objects.related_field('abc').related_field('abc')

        assert file in result

    def test_chaining_different_related_fields_returns_empty(self) -> None:
        create_test_file(related_field='abc')

        result = File.objects.related_field('abc').related_field('xyz')

        assert result.count() == 0

    def test_active_combined_with_standard_filter(self) -> None:
        ticket = create_test_helpdesk_ticket()
        content_type = ContentType.objects.get_for_model(ticket)
        file = create_test_file(
            content_type=content_type,
            object_id=ticket.pk,
        )
        deleted = create_test_file(
            content_type=content_type,
            object_id=ticket.pk,
            is_deleted=True,
        )

        result = File.objects.active().filter(
            content_type=content_type,
            object_id=ticket.pk,
        )

        assert file in result
        assert deleted not in result
