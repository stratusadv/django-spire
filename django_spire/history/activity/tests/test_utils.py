from __future__ import annotations

from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.history.activity.models import Activity
from django_spire.history.activity.utils import add_activity, add_bulk_activity, add_form_activity

from test_project.app.task.models import Task


class TestAddFormActivity(TestCase):
    def setUp(self) -> None:
        self.super_user = AuthUser.objects.create_superuser(
            username='superuser', first_name='Super', last_name='User'
        )

    def test_add_form_activity_created(self) -> None:
        pk = 0
        user = get_object_or_null_obj(AuthUser, pk=pk)
        user.username = 'newuser'
        user.first_name = 'New'
        user.last_name = 'User'
        user.save()

        add_form_activity(user, pk=pk, user=self.super_user)

        assert Activity.objects.count() == 1
        activity = Activity.objects.first()
        assert activity is not None
        assert activity.verb == 'created'
        assert 'created' in activity.information
        assert 'Super User' in activity.information
        assert 'Auth User' in activity.information

    def test_add_form_activity_updated(self) -> None:
        user = get_object_or_null_obj(AuthUser, pk=0)
        user.username = 'updateuser'
        user.first_name = 'Update'
        user.last_name = 'User'
        user.save()

        add_form_activity(user, pk=user.pk, user=self.super_user)

        assert Activity.objects.count() == 1
        activity = Activity.objects.first()
        assert activity is not None
        assert activity.verb == 'updated'
        assert 'updated' in activity.information
        assert 'Super User' in activity.information
        assert 'Auth User' in activity.information

    def test_add_form_activity_multiple_calls(self) -> None:
        pk = 0
        user_1 = get_object_or_null_obj(AuthUser, pk=pk)
        user_1.username = 'user1'
        user_1.first_name = 'First'
        user_1.last_name = 'User'
        user_1.save()

        user_2 = get_object_or_null_obj(AuthUser, pk=pk)
        user_2.username = 'user2'
        user_2.first_name = 'Second'
        user_2.last_name = 'User'
        user_2.save()

        add_form_activity(user_1, pk=pk, user=self.super_user)
        add_form_activity(user_2, pk=user_2.pk, user=self.super_user)

        assert Activity.objects.count() == 2
        activities = Activity.objects.all().order_by('pk')
        assert activities[0].verb == 'created'
        assert 'created' in activities[0].information
        assert activities[1].verb == 'updated'
        assert 'updated' in activities[1].information


class TestAddActivity(TestCase):
    def setUp(self) -> None:
        self.super_user = AuthUser.objects.create_superuser(
            username='superuser', first_name='Super', last_name='User'
        )

    def test_add_activity_creates_row(self) -> None:
        task = Task.objects.create(name='One')

        activity = add_activity(task, self.super_user, 'archived')

        assert Activity.objects.count() == 1
        assert activity.verb == 'archived'
        assert activity.user == self.super_user
        assert activity.object_id == task.pk
        assert 'Super User archived' in activity.information
        assert 'One' in activity.information


class TestAddBulkActivity(TestCase):
    def setUp(self) -> None:
        self.super_user = AuthUser.objects.create_superuser(
            username='superuser', first_name='Super', last_name='User'
        )
        self.task_1 = Task.objects.create(name='One')
        self.task_2 = Task.objects.create(name='Two')

    def test_creates_row_per_instance(self) -> None:
        activities = add_bulk_activity([self.task_1, self.task_2], self.super_user, 'updated')

        assert len(activities) == 2
        assert Activity.objects.count() == 2
        assert {activity.object_id for activity in activities} == {self.task_1.pk, self.task_2.pk}
        assert all(activity.verb == 'updated' for activity in activities)
        assert all(activity.user == self.super_user for activity in activities)

    def test_rows_carry_content_type_and_information(self) -> None:
        activities = add_bulk_activity([self.task_1], self.super_user, 'updated')

        activity = activities[0]
        assert activity.content_type == ContentType.objects.get_for_model(Task)
        assert 'Super User updated' in activity.information
        assert 'One' in activity.information

    def test_empty_instances_return_empty_list(self) -> None:
        activities = add_bulk_activity([], self.super_user, 'updated')

        assert activities == []
        assert Activity.objects.count() == 0

    def test_unsaved_instances_are_skipped(self) -> None:
        unsaved = Task(name='Unsaved')

        activities = add_bulk_activity([self.task_1, unsaved], self.super_user, 'created')

        assert len(activities) == 1
        assert activities[0].object_id == self.task_1.pk

    def test_caps_at_count_max(self) -> None:
        with patch('django_spire.history.activity.utils.BULK_ACTIVITY_COUNT_MAX', 1):
            activities = add_bulk_activity([self.task_1, self.task_2], self.super_user, 'updated')

        assert len(activities) == 1
        assert Activity.objects.count() == 1
