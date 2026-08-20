from __future__ import annotations

from django.test import TestCase

from django_spire.auth.user.models import AuthUser
from django_spire.history.activity.context import set_current_user
from django_spire.history.activity.models import Activity

from test_project.app.task.models import Task


class HistoryQuerySetTestCase(TestCase):
    def setUp(self) -> None:
        self.active_task = Task.objects.create(name='Active')
        self.inactive_task = Task.objects.create(name='Inactive', is_active=False)
        self.deleted_task = Task.objects.create(name='Deleted', is_deleted=True)

        self.inactive_deleted_task = Task.objects.create(
            name='Inactive Deleted',
            is_active=False,
            is_deleted=True,
        )

    def tearDown(self) -> None:
        set_current_user(None)


class TestHistoryQuerySetFilters(HistoryQuerySetTestCase):
    def test_active_excludes_inactive_and_deleted(self) -> None:
        assert list(Task.objects.active()) == [self.active_task]

    def test_inactive_excludes_active_and_deleted(self) -> None:
        assert list(Task.objects.inactive()) == [self.inactive_task]

    def test_deleted_includes_inactive_deleted_rows(self) -> None:
        deleted_pks = set(Task.objects.deleted().values_list('pk', flat=True))
        expected_pks = {self.deleted_task.pk, self.inactive_deleted_task.pk}

        assert deleted_pks == expected_pks

    def test_not_deleted_includes_inactive_rows(self) -> None:
        not_deleted_pks = set(Task.objects.not_deleted().values_list('pk', flat=True))
        expected_pks = {self.active_task.pk, self.inactive_task.pk}

        assert not_deleted_pks == expected_pks

    def test_filters_chain(self) -> None:
        chained = Task.objects.not_deleted().filter(name='Active')

        assert list(chained) == [self.active_task]

    def test_filters_are_unaffected_by_an_active_user(self) -> None:
        user = AuthUser.objects.create_user(username='filteractor')

        set_current_user(user)

        assert list(Task.objects.active()) == [self.active_task]


class TestHistoryQuerySetReturnValues(HistoryQuerySetTestCase):
    def test_bulk_create_returns_the_created_objects(self) -> None:
        created = Task.objects.bulk_create([Task(name='One'), Task(name='Two')])

        assert len(created) == 2
        assert all(task.pk is not None for task in created)
        assert Activity.objects.count() == 0

    def test_bulk_update_returns_the_updated_count(self) -> None:
        self.active_task.description = 'Changed'

        updated_count = Task.objects.bulk_update([self.active_task], ['description'])

        assert updated_count == 1
        assert Activity.objects.count() == 0

    def test_update_returns_the_updated_count(self) -> None:
        updated_count = Task.objects.not_deleted().update(description='Changed')

        assert updated_count == 2
        assert Activity.objects.count() == 0

    def test_delete_returns_the_deleted_counts(self) -> None:
        deleted_count, deleted_by_model = Task.objects.filter(pk=self.active_task.pk).delete()

        assert deleted_by_model[Task._meta.label] == 1
        assert deleted_count >= 1
        assert Activity.objects.count() == 0

    def test_bulk_create_with_ignore_conflicts_returns_objects(self) -> None:
        created = Task.objects.bulk_create([Task(name='One')], ignore_conflicts=True)

        assert len(created) == 1
        assert Activity.objects.count() == 0

    def test_empty_update_returns_zero(self) -> None:
        assert Task.objects.filter(name='Missing').update(description='Changed') == 0
