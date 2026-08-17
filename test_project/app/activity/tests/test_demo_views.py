from __future__ import annotations

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from django_spire.auth.group.models import AuthGroup
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.history.activity.context import set_current_user
from django_spire.history.activity.models import Activity

from test_project.app.activity.views import (
    DEMO_GROUP_NAME,
    DEMO_MEMBER_PREFIX,
    DEMO_MEMBER_USERNAME,
    DEMO_TASK_PREFIX
)
from test_project.app.task.models import Task


class ActivityDemoTestCase(BaseTestCase):
    def tearDown(self) -> None:
        set_current_user(None)

    def act(self, action: str):
        return self.client.post(reverse(f'activity:{action}'))

    def demo_page(self):
        return self.client.get(reverse('activity:demo'))

    def demo_tasks(self):
        return Task.objects.filter(name__startswith=DEMO_TASK_PREFIX)

    def verb_count(self, verb: str) -> int:
        return Activity.objects.filter(verb=verb).count()


class TestDemoPage(ActivityDemoTestCase):
    def test_renders_an_empty_feed(self) -> None:
        response = self.demo_page()

        assert response.status_code == 200
        assert response.context['activity_count'] == 0
        assert response.context['task_count'] == 0
        assert response.context['task_deleted_count'] == 0
        assert response.context['group_member_count'] == 0
        assert response.context['member_in_group'] is False

    def test_lists_activities_after_an_action(self) -> None:
        self.act('create')

        response = self.demo_page()

        assert response.context['activity_count'] == 1
        assert response.context['task_count'] == 1
        assert len(response.context['activities']) == 1
        assert response.context['activities'][0].verb == 'created'

    def test_counts_soft_deleted_tasks(self) -> None:
        self.act('create')
        self.act('soft_delete')

        response = self.demo_page()

        assert response.context['task_count'] == 1
        assert response.context['task_deleted_count'] == 1

    def test_counts_group_members(self) -> None:
        self.act('member_add')
        self.act('member_add_many')

        assert self.demo_page().context['group_member_count'] == 4

    def test_requires_login(self) -> None:
        client = Client()

        response = client.get(reverse('activity:demo'))

        assert response.status_code == 302


class TestDemoCreate(ActivityDemoTestCase):
    def test_post_creates_a_task_and_logs_created(self) -> None:
        response = self.act('create')

        assert response.status_code == 302
        assert self.demo_tasks().count() == 1
        assert self.verb_count('created') == 1

    def test_activity_is_attributed_to_the_request_user(self) -> None:
        self.act('create')

        assert Activity.objects.first().user == self.super_user

    def test_get_changes_nothing(self) -> None:
        response = self.client.get(reverse('activity:create'))

        assert response.status_code == 302
        assert self.demo_tasks().count() == 0
        assert Activity.objects.count() == 0

    def test_requires_login(self) -> None:
        client = Client()

        response = client.post(reverse('activity:create'))

        assert response.status_code == 302
        assert self.demo_tasks().count() == 0
        assert Activity.objects.count() == 0


class TestDemoUpdate(ActivityDemoTestCase):
    def test_post_logs_updated(self) -> None:
        self.act('create')
        self.act('update')

        assert self.verb_count('updated') == 1

    def test_post_without_tasks_logs_nothing(self) -> None:
        self.act('update')

        assert Activity.objects.count() == 0


class TestDemoSoftDelete(ActivityDemoTestCase):
    def test_post_logs_deleted_and_keeps_the_row(self) -> None:
        self.act('create')
        self.act('soft_delete')

        task = self.demo_tasks().get()

        assert task.is_deleted is True
        assert self.verb_count('deleted') == 1
        assert self.verb_count('updated') == 0

    def test_post_without_tasks_logs_nothing(self) -> None:
        self.act('soft_delete')

        assert Activity.objects.count() == 0


class TestDemoRestore(ActivityDemoTestCase):
    def test_post_logs_updated_and_clears_the_deleted_flag(self) -> None:
        self.act('create')
        self.act('soft_delete')
        Activity.objects.all().delete()

        self.act('restore')

        task = self.demo_tasks().get()

        assert task.is_deleted is False
        assert self.verb_count('updated') == 1
        assert self.verb_count('deleted') == 0

    def test_post_without_deleted_tasks_logs_nothing(self) -> None:
        self.act('create')
        Activity.objects.all().delete()

        self.act('restore')

        assert Activity.objects.count() == 0


class TestDemoCascadeDelete(ActivityDemoTestCase):
    def test_child_create_attaches_to_the_oldest_task(self) -> None:
        self.act('create')
        self.act('child_create')

        parent = self.demo_tasks().order_by('pk').first()
        child = self.demo_tasks().order_by('-pk').first()

        assert self.demo_tasks().count() == 2
        assert child.parent == parent

    def test_child_create_without_tasks_logs_nothing(self) -> None:
        self.act('child_create')

        assert self.demo_tasks().count() == 0
        assert Activity.objects.count() == 0

    def test_post_logs_the_parent_and_the_child(self) -> None:
        self.act('create')
        self.act('child_create')

        self.act('cascade_delete')

        assert self.demo_tasks().count() == 0
        assert self.verb_count('deleted') == 2
        assert self.verb_count('created') == 0

    def test_post_without_tasks_logs_nothing(self) -> None:
        self.act('cascade_delete')

        assert Activity.objects.count() == 0


class TestDemoUnattributedCreate(ActivityDemoTestCase):
    def test_post_creates_a_task_without_activity(self) -> None:
        self.act('unattributed_create')

        assert self.demo_tasks().count() == 1
        assert Activity.objects.count() == 0

    def test_only_the_attributed_create_is_logged(self) -> None:
        self.act('create')
        self.act('unattributed_create')

        assert self.demo_tasks().count() == 2
        assert Activity.objects.count() == 1


class TestDemoHardDelete(ActivityDemoTestCase):
    def test_post_removes_the_row_and_logs_deleted(self) -> None:
        self.act('create')
        self.act('hard_delete')

        assert self.demo_tasks().count() == 0
        assert self.verb_count('deleted') == 1

    def test_post_discards_the_prior_activity_of_the_deleted_row(self) -> None:
        self.act('create')
        self.act('hard_delete')

        assert self.verb_count('created') == 0

    def test_post_without_tasks_logs_nothing(self) -> None:
        self.act('hard_delete')

        assert Activity.objects.count() == 0


class TestDemoBulkActions(ActivityDemoTestCase):
    def test_bulk_create_logs_one_activity_per_row(self) -> None:
        self.act('bulk_create')

        assert self.demo_tasks().count() == 3
        assert self.verb_count('created') == 3

    def test_bulk_update_logs_one_activity_per_row(self) -> None:
        self.act('bulk_create')
        Activity.objects.all().delete()

        self.act('bulk_update')

        assert self.verb_count('updated') == 3

    def test_bulk_update_without_tasks_logs_nothing(self) -> None:
        self.act('bulk_update')

        assert Activity.objects.count() == 0

    def test_queryset_update_logs_one_activity_per_row(self) -> None:
        self.act('bulk_create')
        Activity.objects.all().delete()

        self.act('queryset_update')

        assert self.verb_count('updated') == 3

    def test_queryset_delete_logs_one_activity_per_row(self) -> None:
        self.act('bulk_create')
        Activity.objects.all().delete()

        self.act('queryset_delete')

        assert self.demo_tasks().count() == 0
        assert self.verb_count('deleted') == 3


class TestDemoMembership(ActivityDemoTestCase):
    def test_member_add_logs_added_on_the_group(self) -> None:
        self.act('member_add')

        group = AuthGroup.objects.get(name=DEMO_GROUP_NAME)
        added_activities = Activity.objects.filter(verb='added')

        assert group.user_set.count() == 1
        assert added_activities.count() == 1
        assert added_activities.first().object_id == group.pk

    def test_member_add_also_logs_the_group_creation(self) -> None:
        self.act('member_add')

        assert self.verb_count('created') == 1

    def test_member_add_shows_membership_on_the_page(self) -> None:
        self.act('member_add')

        assert self.demo_page().context['member_in_group'] is True

    def test_member_remove_logs_removed(self) -> None:
        self.act('member_add')
        Activity.objects.all().delete()

        self.act('member_remove')

        group = AuthGroup.objects.get(name=DEMO_GROUP_NAME)
        removed_activities = Activity.objects.filter(verb='removed')

        assert group.user_set.count() == 0
        assert removed_activities.count() == 1
        assert removed_activities.first().object_id == group.pk

    def test_member_remove_without_a_group_logs_nothing(self) -> None:
        self.act('member_remove')

        assert Activity.objects.count() == 0

    def test_member_add_many_logs_a_single_counted_activity(self) -> None:
        self.act('member_add')
        Activity.objects.all().delete()

        self.act('member_add_many')

        group = AuthGroup.objects.get(name=DEMO_GROUP_NAME)
        added_activities = Activity.objects.filter(verb='added')

        assert group.user_set.count() == 4
        assert added_activities.count() == 1
        assert 'added 3 users' in added_activities.first().information

    def test_member_clear_logs_a_single_counted_activity(self) -> None:
        self.act('member_add')
        self.act('member_add_many')
        Activity.objects.all().delete()

        self.act('member_clear')

        group = AuthGroup.objects.get(name=DEMO_GROUP_NAME)
        removed_activities = Activity.objects.filter(verb='removed')

        assert group.user_set.count() == 0
        assert removed_activities.count() == 1
        assert 'removed 4 users' in removed_activities.first().information

    def test_member_clear_without_a_group_logs_nothing(self) -> None:
        self.act('member_clear')

        assert Activity.objects.count() == 0


class TestDemoReset(ActivityDemoTestCase):
    def test_post_clears_every_demo_row(self) -> None:
        self.act('bulk_create')
        self.act('member_add')
        self.act('member_add_many')

        self.act('reset')

        assert self.demo_tasks().count() == 0
        assert AuthGroup.objects.filter(name=DEMO_GROUP_NAME).count() == 0
        assert User.objects.filter(username=DEMO_MEMBER_USERNAME).count() == 0
        assert User.objects.filter(username__startswith=DEMO_MEMBER_PREFIX).count() == 0
        assert Activity.objects.count() == 0

    def test_post_on_an_empty_demo_leaves_nothing_behind(self) -> None:
        self.act('reset')

        assert Activity.objects.count() == 0


class TestDemoWalkthrough(ActivityDemoTestCase):
    def test_every_action_logs_the_expected_verbs(self) -> None:
        self.act('create')
        assert self.verb_count('created') == 1

        self.act('update')
        assert self.verb_count('updated') == 1

        self.act('bulk_create')
        assert self.verb_count('created') == 4

        self.act('bulk_update')
        assert self.verb_count('updated') == 4

        self.act('queryset_update')
        assert self.verb_count('updated') == 8

        self.act('soft_delete')
        assert self.verb_count('deleted') == 1
        assert self.verb_count('updated') == 8

        self.act('restore')
        assert self.verb_count('deleted') == 1
        assert self.verb_count('updated') == 9

        self.act('hard_delete')
        assert self.verb_count('deleted') == 2

        self.act('queryset_delete')
        assert self.verb_count('deleted') == 4

        self.act('member_add')
        assert self.verb_count('added') == 1
        assert self.demo_page().context['member_in_group'] is True

        self.act('member_add_many')
        assert self.verb_count('added') == 2

        self.act('member_remove')
        assert self.verb_count('removed') == 1
        assert self.demo_page().context['member_in_group'] is False

        self.act('member_clear')
        assert self.verb_count('removed') == 2

        self.act('reset')
        assert Activity.objects.count() == 0

    def test_every_activity_is_attributed_to_the_request_user(self) -> None:
        self.act('create')
        self.act('update')
        self.act('bulk_create')
        self.act('bulk_update')
        self.act('queryset_update')
        self.act('soft_delete')
        self.act('member_add')

        activity_users = set(Activity.objects.values_list('user_id', flat=True))

        assert Activity.objects.count() > 0
        assert activity_users == {self.super_user.pk}
