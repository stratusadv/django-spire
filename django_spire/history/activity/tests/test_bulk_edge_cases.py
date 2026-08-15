from __future__ import annotations

import pytest

from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from django.db.models import QuerySet
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from django_spire.auth.user.models import AuthUser
from django_spire.comment.models import Comment
from django_spire.history.activity.context import set_current_user
from django_spire.history.activity.models import Activity

from test_project.app.task.models import Task


class BulkEdgeTestCase(TestCase):
    def setUp(self) -> None:
        self.user = AuthUser.objects.create_user(
            username='bulkedgeactor',
            first_name='Bulk',
            last_name='Actor',
        )

    def tearDown(self) -> None:
        set_current_user(None)


class TestBulkUpdateEdgeCases(BulkEdgeTestCase):
    def test_batch_size_logs_every_row(self) -> None:
        tasks = [Task.objects.create(name=f'Task {index}') for index in range(5)]

        set_current_user(self.user)

        for task in tasks:
            task.description = 'Changed'

        Task.objects.bulk_update(tasks, ['description'], batch_size=2)

        assert Activity.objects.filter(verb='updated').count() == 5

    def test_duplicate_objects_log_one_activity_per_row(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.description = 'Changed'
        duplicated_tasks = [task, task]

        Task.objects.bulk_update(duplicated_tasks, ['description'])

        assert Activity.objects.filter(verb='updated').count() == 1

    def test_unsaved_object_raises_and_logs_nothing(self) -> None:
        set_current_user(self.user)

        unsaved_tasks = [Task(name='Unsaved')]

        with pytest.raises(ValueError, match='primary key'):
            Task.objects.bulk_update(unsaved_tasks, ['name'])

        assert Activity.objects.count() == 0

    def test_empty_field_list_raises_and_logs_nothing(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        with pytest.raises(ValueError, match='Field names must be given'):
            Task.objects.bulk_update([task], [])

        assert Activity.objects.count() == 0

    def test_restricted_queryset_skips_rows_outside_it(self) -> None:
        active_task = Task.objects.create(name='Active')
        inactive_task = Task.objects.create(name='Inactive', is_active=False)

        set_current_user(self.user)

        active_task.description = 'Changed'
        inactive_task.description = 'Changed'
        tasks = [active_task, inactive_task]

        Task.objects.active().bulk_update(tasks, ['description'])

        activities = Activity.objects.filter(verb='updated')

        assert activities.count() == 1
        assert activities.first().object_id == active_task.pk

    def test_audit_failure_rolls_back_the_write(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)
        message = 'bulk update audit insert failed'

        target = 'django_spire.history.activity.utils.add_bulk_activity'
        task.description = 'Changed'

        with (
            pytest.raises(RuntimeError, match=message),
            patch(target, side_effect=RuntimeError(message)),
        ):
            Task.objects.bulk_update([task], ['description'])

        task.refresh_from_db()

        assert task.description == ''
        assert Activity.objects.count() == 0


class TestBulkCreateEdgeCases(BulkEdgeTestCase):
    def test_explicit_primary_keys_log_each_row(self) -> None:
        set_current_user(self.user)

        tasks = [Task(pk=900001, name='One'), Task(pk=900002, name='Two')]
        Task.objects.bulk_create(tasks)

        object_ids = set(Activity.objects.values_list('object_id', flat=True))

        assert object_ids == {900001, 900002}

    def test_large_batch_logs_one_activity_per_row(self) -> None:
        set_current_user(self.user)

        tasks = [Task(name=f'Task {index}') for index in range(250)]
        Task.objects.bulk_create(tasks)

        assert Activity.objects.filter(verb='created').count() == 250

    def test_audit_failure_rolls_back_the_insert(self) -> None:
        set_current_user(self.user)
        message = 'bulk create audit insert failed'

        target = 'django_spire.history.activity.utils.add_bulk_activity'

        with (
            pytest.raises(RuntimeError, match=message),
            patch(target, side_effect=RuntimeError(message)),
        ):
            Task.objects.bulk_create([Task(name='One')])

        assert Task.objects.count() == 0
        assert Activity.objects.count() == 0

    def test_rolled_back_savepoint_discards_rows_and_activity(self) -> None:
        set_current_user(self.user)
        message = 'inner rollback'

        def create_then_fail() -> None:
            Task.objects.bulk_create([Task(name='One')])

            raise RuntimeError(message)

        with pytest.raises(RuntimeError, match=message), transaction.atomic():
            create_then_fail()

        assert Task.objects.count() == 0
        assert Activity.objects.count() == 0


class TestUpdateEdgeCases(BulkEdgeTestCase):
    def test_warns_when_fewer_rows_change_than_were_snapshotted(self) -> None:
        Task.objects.create(name='One')
        Task.objects.create(name='Two')

        set_current_user(self.user)

        logger_name = 'django_spire.history.querysets'

        with (
            patch.object(QuerySet, 'update', return_value=0),
            self.assertLogs(logger_name, level='WARNING') as logs,
        ):
            Task.objects.update(description='Changed')

        assert 'snapshotted' in logs.output[0]

    def test_filtered_through_a_relation_logs_only_matched_rows(self) -> None:
        parent = Task.objects.create(name='Parent')
        child = Task.objects.create(name='Child', parent=parent)

        set_current_user(self.user)

        Task.objects.filter(parent__name='Parent').update(description='Changed')

        activities = Activity.objects.filter(verb='updated')

        assert activities.count() == 1
        assert activities.first().object_id == child.pk

    def test_repeated_updates_log_each_time(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        Task.objects.filter(pk=task.pk).update(description='First')
        Task.objects.filter(pk=task.pk).update(description='Second')

        assert Activity.objects.filter(verb='updated').count() == 2

    def test_explicit_connection_alias_logs(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        Task.objects.using('default').filter(pk=task.pk).update(description='Changed')

        assert Activity.objects.filter(verb='updated').count() == 1

    def test_rolled_back_transaction_discards_the_update_and_activity(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)
        message = 'update rollback'

        def update_then_fail() -> None:
            Task.objects.filter(pk=task.pk).update(description='Changed')

            raise RuntimeError(message)

        with pytest.raises(RuntimeError, match=message), transaction.atomic():
            update_then_fail()

        task.refresh_from_db()

        assert task.description == ''
        assert Activity.objects.count() == 0


class TestQuerysetDeleteEdgeCases(BulkEdgeTestCase):
    def test_returns_the_deleted_row_counts(self) -> None:
        task_one = Task.objects.create(name='One')
        task_two = Task.objects.create(name='Two')
        target_pks = [task_one.pk, task_two.pk]

        set_current_user(self.user)

        deleted_count, deleted_by_model = Task.objects.filter(pk__in=target_pks).delete()

        assert deleted_by_model[Task._meta.label] == 2
        assert deleted_count >= 2
        assert Activity.objects.filter(verb='deleted').count() == 2

    def test_explicit_connection_alias_logs(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        Task.objects.using('default').filter(pk=task.pk).delete()

        assert Activity.objects.filter(verb='deleted').count() == 1

    def test_filtered_through_a_relation_logs_only_matched_rows(self) -> None:
        parent = Task.objects.create(name='Parent')
        child = Task.objects.create(name='Child', parent=parent)
        child_pk = child.pk

        set_current_user(self.user)

        Task.objects.filter(parent__name='Parent').delete()

        activities = Activity.objects.filter(verb='deleted')

        assert activities.count() == 1
        assert activities.first().object_id == child_pk
        assert Task.objects.filter(pk=parent.pk).exists()

    def test_rolled_back_transaction_discards_the_delete_and_activity(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)
        message = 'delete rollback'

        def delete_then_fail() -> None:
            Task.objects.filter(pk=task.pk).delete()

            raise RuntimeError(message)

        with pytest.raises(RuntimeError, match=message), transaction.atomic():
            delete_then_fail()

        assert Task.objects.filter(pk=task.pk).exists()
        assert Activity.objects.count() == 0


class TestUnauditedModelBulkOperations(BulkEdgeTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.task = Task.objects.create(name='One')

        self.comment = Comment.objects.create(
            content_type=ContentType.objects.get_for_model(Task),
            object_id=self.task.pk,
            user=self.user,
            information='hello',
        )

    def test_bulk_update_logs_nothing(self) -> None:
        set_current_user(self.user)

        self.comment.information = 'changed'
        Comment.objects.bulk_update([self.comment], ['information'])

        assert Activity.objects.count() == 0

    def test_queryset_update_logs_nothing(self) -> None:
        set_current_user(self.user)

        Comment.objects.filter(pk=self.comment.pk).update(information='changed')

        assert Activity.objects.count() == 0

    def test_queryset_delete_logs_nothing(self) -> None:
        set_current_user(self.user)

        Comment.objects.filter(pk=self.comment.pk).delete()

        assert Activity.objects.count() == 0


class TestBulkQueryCount(BulkEdgeTestCase):
    def bulk_create_query_count(self, count: int) -> int:
        tasks = [Task(name=f'Task {index}') for index in range(count)]

        with CaptureQueriesContext(connection) as context:
            Task.objects.bulk_create(tasks)

        return len(context.captured_queries)

    def delete_query_count(self, count: int) -> int:
        tasks = [Task.objects.create(name=f'Task {index}') for index in range(count)]
        target_pks = [task.pk for task in tasks]

        with CaptureQueriesContext(connection) as context:
            Task.objects.filter(pk__in=target_pks).delete()

        return len(context.captured_queries)

    def update_query_count(self, count: int) -> int:
        tasks = [Task.objects.create(name=f'Task {index}') for index in range(count)]
        target_pks = [task.pk for task in tasks]

        with CaptureQueriesContext(connection) as context:
            Task.objects.filter(pk__in=target_pks).update(description='Changed')

        return len(context.captured_queries)

    def test_bulk_create_query_count_does_not_grow_with_rows(self) -> None:
        ContentType.objects.get_for_model(Task)

        set_current_user(self.user)

        self.bulk_create_query_count(2)

        assert self.bulk_create_query_count(2) == self.bulk_create_query_count(20)

    def test_update_query_count_does_not_grow_with_rows(self) -> None:
        ContentType.objects.get_for_model(Task)

        set_current_user(self.user)

        self.update_query_count(2)

        assert self.update_query_count(2) == self.update_query_count(20)

    def test_delete_query_count_does_not_grow_with_rows(self) -> None:
        ContentType.objects.get_for_model(Task)

        set_current_user(self.user)

        self.delete_query_count(2)

        assert self.delete_query_count(2) == self.delete_query_count(20)
