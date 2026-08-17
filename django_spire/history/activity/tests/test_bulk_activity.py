from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth.models import User
from django.db.models import Case, Value, When
from django.test import TestCase

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.models import AuthUser
from django_spire.history.activity.context import set_current_user
from django_spire.history.activity.models import Activity
from django_spire.history.querysets import HistoryQuerySet

from test_project.app.task.models import Task


class BulkActivityTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',  # noqa: S106
            first_name='Test',
            last_name='User',
        )

    def tearDown(self) -> None:
        set_current_user(None)


class TestBulkCreateActivity(BulkActivityTestCase):
    def test_bulk_create_creates_activities(self) -> None:
        set_current_user(self.user)

        tasks = Task.objects.bulk_create([Task(name='One'), Task(name='Two')])

        activities = Activity.objects.filter(verb='created')

        assert activities.count() == 2
        assert {activity.object_id for activity in activities} == {task.pk for task in tasks}
        assert all(activity.user == self.user for activity in activities)
        assert 'Test User created' in activities.first().information

    def test_bulk_create_without_user_creates_nothing(self) -> None:
        Task.objects.bulk_create([Task(name='One')])

        assert Activity.objects.count() == 0

    def test_bulk_create_respects_count_max(self) -> None:
        set_current_user(self.user)

        with patch('django_spire.history.activity.utils.BULK_ACTIVITY_COUNT_MAX', 2):
            tasks = Task.objects.bulk_create(
                [Task(name='One'), Task(name='Two'), Task(name='Three')]
            )

        assert len(tasks) == 3
        assert Activity.objects.count() == 2

    def test_bulk_create_update_conflicts_warns_and_logs_nothing(self) -> None:
        set_current_user(self.user)

        with self.assertLogs('django_spire.history.querysets', level='WARNING') as logs:
            Task.objects.bulk_create(
                [Task(name='One')],
                update_conflicts=True,
                unique_fields=['id'],
                update_fields=['description'],
            )

        assert Activity.objects.count() == 0
        assert 'update_conflicts' in logs.output[0]


class TestBulkUpdateActivity(BulkActivityTestCase):
    def test_bulk_update_creates_activities(self) -> None:
        tasks = [Task.objects.create(name='One'), Task.objects.create(name='Two')]

        set_current_user(self.user)

        for task in tasks:
            task.name = f'{task.name} Renamed'

        Task.objects.bulk_update(tasks, ['name'])

        activities = Activity.objects.filter(verb='updated')

        assert activities.count() == 2
        assert {activity.object_id for activity in activities} == {task.pk for task in tasks}
        assert 'Renamed' in activities.first().information

    def test_bulk_update_without_user_creates_nothing(self) -> None:
        task = Task.objects.create(name='One')
        task.name = 'Renamed'

        Task.objects.bulk_update([task], ['name'])

        assert Activity.objects.count() == 0


class TestUpdateActivity(BulkActivityTestCase):
    def test_update_creates_activities(self) -> None:
        tasks = [Task.objects.create(name='One'), Task.objects.create(name='Two')]

        set_current_user(self.user)

        updated_count = Task.objects.filter(pk__in=[task.pk for task in tasks]).update(
            description='Changed'
        )

        activities = Activity.objects.filter(verb='updated')

        assert updated_count == 2
        assert activities.count() == 2
        assert {activity.object_id for activity in activities} == {task.pk for task in tasks}

    def test_update_without_user_creates_nothing(self) -> None:
        Task.objects.create(name='One')

        updated_count = Task.objects.update(description='Changed')

        assert updated_count == 1
        assert Activity.objects.count() == 0

    def test_update_respects_count_max(self) -> None:
        Task.objects.create(name='One')
        Task.objects.create(name='Two')
        Task.objects.create(name='Three')

        set_current_user(self.user)

        with patch('django_spire.history.activity.utils.BULK_ACTIVITY_COUNT_MAX', 2):
            updated_count = Task.objects.update(description='Changed')

        assert updated_count == 3
        assert Activity.objects.count() == 2

    def test_update_on_filtered_out_rows_creates_nothing(self) -> None:
        Task.objects.create(name='One')

        set_current_user(self.user)

        updated_count = Task.objects.filter(name='Missing').update(description='Changed')

        assert updated_count == 0
        assert Activity.objects.count() == 0


class TestUpdateSoftDeleteActivity(BulkActivityTestCase):
    def test_update_is_deleted_true_logs_deleted(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        Task.objects.filter(pk=task.pk).update(is_deleted=True)

        deleted_activities = Activity.objects.filter(verb='deleted')

        assert deleted_activities.count() == 1
        assert deleted_activities.first().object_id == task.pk
        assert 'Test User deleted' in deleted_activities.first().information
        assert Activity.objects.filter(verb='updated').count() == 0

    def test_update_is_deleted_true_on_already_deleted_logs_updated(self) -> None:
        task = Task.objects.create(name='One')
        Task.objects.filter(pk=task.pk).update(is_deleted=True)

        set_current_user(self.user)

        Task.objects.filter(pk=task.pk).update(is_deleted=True)

        assert Activity.objects.filter(verb='deleted').count() == 0
        assert Activity.objects.filter(verb='updated').count() == 1

    def test_update_is_deleted_mixed_splits_verbs(self) -> None:
        task_live = Task.objects.create(name='Live')
        task_gone = Task.objects.create(name='Gone', is_deleted=True)

        set_current_user(self.user)

        target_pks = [task_live.pk, task_gone.pk]
        Task.objects.filter(pk__in=target_pks).update(is_deleted=True)

        deleted_activities = Activity.objects.filter(verb='deleted')
        updated_activities = Activity.objects.filter(verb='updated')

        assert deleted_activities.count() == 1
        assert deleted_activities.first().object_id == task_live.pk
        assert updated_activities.count() == 1
        assert updated_activities.first().object_id == task_gone.pk

    def test_update_is_deleted_value_expression_logs_deleted(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        Task.objects.filter(pk=task.pk).update(is_deleted=Value(value=True))

        assert Activity.objects.filter(verb='deleted').count() == 1
        assert Activity.objects.filter(verb='updated').count() == 0

    def test_update_is_deleted_case_expression_splits_verbs(self) -> None:
        task_live = Task.objects.create(name='Live')
        task_gone = Task.objects.create(name='Gone', is_deleted=True)

        set_current_user(self.user)

        is_deleted_case = Case(
            When(name='Live', then=Value(value=True)),
            default=Value(value=True),
        )

        target_pks = [task_live.pk, task_gone.pk]
        Task.objects.filter(pk__in=target_pks).update(is_deleted=is_deleted_case)

        deleted_activities = Activity.objects.filter(verb='deleted')
        updated_activities = Activity.objects.filter(verb='updated')

        assert deleted_activities.count() == 1
        assert deleted_activities.first().object_id == task_live.pk
        assert updated_activities.count() == 1
        assert updated_activities.first().object_id == task_gone.pk

    def test_update_is_deleted_false_logs_updated(self) -> None:
        task = Task.objects.create(name='One', is_deleted=True)

        set_current_user(self.user)

        Task.objects.filter(pk=task.pk).update(is_deleted=False)

        assert Activity.objects.filter(verb='deleted').count() == 0
        assert Activity.objects.filter(verb='updated').count() == 1

    def test_bulk_update_is_deleted_true_logs_deleted(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.is_deleted = True
        Task.objects.bulk_update([task], ['is_deleted'])

        assert Activity.objects.filter(verb='deleted').count() == 1
        assert Activity.objects.filter(verb='updated').count() == 0

    def test_bulk_update_is_deleted_on_already_deleted_logs_updated(self) -> None:
        task = Task.objects.create(name='One', is_deleted=True)

        set_current_user(self.user)

        task.description = 'Changed'
        Task.objects.bulk_update([task], ['description', 'is_deleted'])

        assert Activity.objects.filter(verb='deleted').count() == 0
        assert Activity.objects.filter(verb='updated').count() == 1

    def test_bulk_update_mixed_is_deleted_splits_verbs(self) -> None:
        task_live = Task.objects.create(name='Live')
        task_gone = Task.objects.create(name='Gone', is_deleted=True)

        set_current_user(self.user)

        task_live.is_deleted = True
        Task.objects.bulk_update([task_live, task_gone], ['is_deleted'])

        deleted_activities = Activity.objects.filter(verb='deleted')
        updated_activities = Activity.objects.filter(verb='updated')

        assert deleted_activities.count() == 1
        assert deleted_activities.first().object_id == task_live.pk
        assert updated_activities.count() == 1
        assert updated_activities.first().object_id == task_gone.pk

    def test_bulk_update_without_is_deleted_field_logs_updated(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.description = 'Changed'
        Task.objects.bulk_update([task], ['description'])

        assert Activity.objects.filter(verb='updated').count() == 1
        assert Activity.objects.filter(verb='deleted').count() == 0


class TestM2MActivity(TestCase):
    def setUp(self) -> None:
        self.auth_user = AuthUser.objects.create_user(
            username='m2muser',
            password='testpass',  # noqa: S106
            first_name='Member',
            last_name='User',
        )
        self.group = AuthGroup.objects.create(name='Editors')

    def tearDown(self) -> None:
        set_current_user(None)

    def test_add_creates_activity(self) -> None:
        set_current_user(self.auth_user)

        self.auth_user.groups.add(self.group)

        activities = Activity.objects.filter(verb='added')

        assert activities.count() == 1
        activity = activities.first()
        assert activity.object_id == self.auth_user.pk
        assert 'added 1 group to' in activity.information

    def test_remove_creates_activity(self) -> None:
        self.auth_user.groups.add(self.group)

        set_current_user(self.auth_user)

        self.auth_user.groups.remove(self.group)

        activities = Activity.objects.filter(verb='removed')

        assert activities.count() == 1
        assert 'removed 1 group from' in activities.first().information

    def test_add_without_user_creates_nothing(self) -> None:
        self.auth_user.groups.add(self.group)

        assert Activity.objects.filter(verb='added').count() == 0

    def test_clear_creates_removed_activity(self) -> None:
        other_group = AuthGroup.objects.create(name='Reviewers')
        self.auth_user.groups.add(self.group, other_group)

        set_current_user(self.auth_user)

        self.auth_user.groups.clear()

        activities = Activity.objects.filter(verb='removed')

        assert activities.count() == 1
        assert activities.first().object_id == self.auth_user.pk
        assert 'removed 2 groups from' in activities.first().information

    def test_clear_when_empty_creates_nothing(self) -> None:
        set_current_user(self.auth_user)

        self.auth_user.groups.clear()

        assert Activity.objects.filter(verb='removed').count() == 0

    def test_clear_without_user_creates_nothing(self) -> None:
        self.auth_user.groups.add(self.group)

        self.auth_user.groups.clear()

        assert Activity.objects.filter(verb='removed').count() == 0

    def test_reverse_clear_creates_removed_activity(self) -> None:
        other_user = AuthUser.objects.create_user(username='otheruser')
        self.group.user_set.set([self.auth_user, other_user])

        set_current_user(self.auth_user)

        self.group.user_set.clear()

        activities = Activity.objects.filter(verb='removed')

        assert activities.count() == 1
        assert activities.first().object_id == self.group.pk
        assert 'removed 2 users from' in activities.first().information

    def test_set_creates_added_and_removed(self) -> None:
        other_group = AuthGroup.objects.create(name='Reviewers')
        self.auth_user.groups.add(self.group)

        set_current_user(self.auth_user)

        self.auth_user.groups.set([other_group])

        assert Activity.objects.filter(verb='added').count() == 1
        assert Activity.objects.filter(verb='removed').count() == 1

    def test_add_information_names_the_group(self) -> None:
        set_current_user(self.auth_user)

        self.auth_user.groups.add(self.group)

        activity = Activity.objects.get(verb='added')

        assert '(Editors)' in activity.information

    def test_remove_information_names_the_group(self) -> None:
        self.auth_user.groups.add(self.group)

        set_current_user(self.auth_user)

        self.auth_user.groups.remove(self.group)

        activity = Activity.objects.get(verb='removed')

        assert '(Editors)' in activity.information

    def test_clear_information_names_the_groups(self) -> None:
        other_group = AuthGroup.objects.create(name='Reviewers')
        self.auth_user.groups.add(self.group, other_group)

        set_current_user(self.auth_user)

        self.auth_user.groups.clear()

        activity = Activity.objects.get(verb='removed')

        assert '(Editors, Reviewers)' in activity.information

    def test_clear_information_truncates_names_beyond_cap(self) -> None:
        groups = [AuthGroup(name=f'Group {index:02d}') for index in range(12)]
        AuthGroup.objects.bulk_create(groups)
        self.auth_user.groups.add(*groups)

        set_current_user(self.auth_user)

        self.auth_user.groups.clear()

        activity = Activity.objects.get(verb='removed')

        assert 'removed 12' in activity.information
        assert 'Group 00' in activity.information
        assert 'and 2 more' in activity.information

    def test_set_with_no_change_creates_nothing(self) -> None:
        self.auth_user.groups.add(self.group)

        set_current_user(self.auth_user)

        self.auth_user.groups.set([self.group])

        assert Activity.objects.filter(verb__in=['added', 'removed']).count() == 0

    def test_set_with_clear_creates_added_and_removed(self) -> None:
        other_group = AuthGroup.objects.create(name='Reviewers')
        self.auth_user.groups.add(self.group)

        set_current_user(self.auth_user)

        self.auth_user.groups.set([other_group], clear=True)

        removed_activities = Activity.objects.filter(verb='removed')
        added_activities = Activity.objects.filter(verb='added')

        assert removed_activities.count() == 1
        assert 'removed 1 group from' in removed_activities.first().information
        assert added_activities.count() == 1
        assert 'added 1 group to' in added_activities.first().information


class TestActivityEnabled(BulkActivityTestCase):
    def test_enabled_for_mixin_model_with_user(self) -> None:
        set_current_user(self.user)

        assert HistoryQuerySet(model=Task)._activity_enabled() is True

    def test_disabled_without_user(self) -> None:
        assert HistoryQuerySet(model=Task)._activity_enabled() is False

    def test_disabled_for_model_without_mixin(self) -> None:
        set_current_user(self.user)

        assert HistoryQuerySet(model=User)._activity_enabled() is False


class TestM2MRemoveAccuracy(TestCase):
    def setUp(self) -> None:
        self.auth_user = AuthUser.objects.create_user(
            username='m2muser',
            password='testpass',  # noqa: S106
            first_name='Member',
            last_name='User',
        )
        self.group = AuthGroup.objects.create(name='Editors')

    def tearDown(self) -> None:
        set_current_user(None)

    def test_remove_non_member_creates_nothing(self) -> None:
        set_current_user(self.auth_user)

        self.auth_user.groups.remove(self.group)

        assert Activity.objects.filter(verb='removed').count() == 0

    def test_add_existing_member_creates_nothing(self) -> None:
        self.auth_user.groups.add(self.group)

        set_current_user(self.auth_user)

        self.auth_user.groups.add(self.group)

        assert Activity.objects.filter(verb='added').count() == 0

    def test_remove_mixed_membership_counts_only_members(self) -> None:
        other_group = AuthGroup.objects.create(name='Reviewers')
        self.auth_user.groups.add(self.group)

        set_current_user(self.auth_user)

        self.auth_user.groups.remove(self.group, other_group)

        activities = Activity.objects.filter(verb='removed')

        assert activities.count() == 1
        assert 'removed 1 group from' in activities.first().information


class TestBulkUpdateAccuracy(BulkActivityTestCase):
    def test_bulk_update_skips_rows_outside_queryset(self) -> None:
        task_active = Task.objects.create(name='Active')
        task_deleted = Task.objects.create(name='Deleted')
        task_deleted.is_deleted = True
        task_deleted.save()

        set_current_user(self.user)

        task_active.description = 'Changed'
        task_deleted.description = 'Changed'

        tasks = [task_active, task_deleted]
        Task.objects.not_deleted().bulk_update(tasks, ['description'])

        activities = Activity.objects.filter(verb='updated')

        assert activities.count() == 1
        assert activities.first().object_id == task_active.pk


class TestBulkActivityWarnings(BulkActivityTestCase):
    def test_bulk_create_ignore_conflicts_warns_when_pks_missing(self) -> None:
        set_current_user(self.user)

        with self.assertLogs('django_spire.history.activity.utils', level='WARNING') as logs:
            Task.objects.bulk_create([Task(name='One')], ignore_conflicts=True)

        assert Activity.objects.count() == 0
        assert 'skipped' in logs.output[0]

    def test_update_over_cap_warns(self) -> None:
        Task.objects.create(name='One')
        Task.objects.create(name='Two')
        Task.objects.create(name='Three')

        set_current_user(self.user)

        with (
            patch('django_spire.history.activity.utils.BULK_ACTIVITY_COUNT_MAX', 2),
            self.assertLogs('django_spire.history.querysets', level='WARNING') as logs,
        ):
            Task.objects.update(description='Changed')

        assert Activity.objects.count() == 2
        assert 'truncated' in logs.output[0]


class TestQuerysetDeleteBulk(BulkActivityTestCase):
    def test_queryset_delete_uses_bulk_insert(self) -> None:
        task_1 = Task.objects.create(name='One')
        task_2 = Task.objects.create(name='Two')

        set_current_user(self.user)

        Task.objects.filter(pk__in=[task_1.pk, task_2.pk]).delete()

        activities = Activity.objects.filter(verb='deleted')

        assert activities.count() == 2
        assert {activity.object_id for activity in activities} == {task_1.pk, task_2.pk}

    def test_queryset_delete_cascade_logs_children(self) -> None:
        parent = Task.objects.create(name='Parent')
        child = Task.objects.create(name='Child', parent=parent)
        parent_pk = parent.pk
        child_pk = child.pk

        set_current_user(self.user)

        Task.objects.filter(pk=parent_pk).delete()

        activities = Activity.objects.filter(verb='deleted')

        assert activities.count() == 2
        assert {activity.object_id for activity in activities} == {parent_pk, child_pk}

    def test_queryset_delete_respects_count_max(self) -> None:
        for name in ('One', 'Two', 'Three'):
            Task.objects.create(name=name)

        set_current_user(self.user)

        with (
            patch('django_spire.history.activity.utils.BULK_ACTIVITY_COUNT_MAX', 2),
            self.assertLogs('django_spire.history.activity.utils', level='WARNING'),
        ):
            Task.objects.all().delete()

        assert Activity.objects.filter(verb='deleted').count() == 2


class TestAuthGroupBulkActivity(BulkActivityTestCase):
    def test_group_bulk_create_creates_activities(self) -> None:
        set_current_user(self.user)

        groups = [AuthGroup(name='One'), AuthGroup(name='Two')]
        AuthGroup.objects.bulk_create(groups)

        assert Activity.objects.filter(verb='created').count() == 2

    def test_group_queryset_update_creates_activities(self) -> None:
        group = AuthGroup.objects.create(name='One')

        set_current_user(self.user)

        AuthGroup.objects.filter(pk=group.pk).update(name='Renamed')

        assert Activity.objects.filter(verb='updated').count() == 1

    def test_group_manager_supports_natural_keys(self) -> None:
        group = AuthGroup.objects.create(name='One')

        assert AuthGroup.objects.get_by_natural_key('One') == group
