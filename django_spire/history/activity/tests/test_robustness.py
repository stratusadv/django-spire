from __future__ import annotations

import asyncio
import threading

import pytest

from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import IntegrityError, connection, transaction
from django.db.models import F, QuerySet
from django.db.models.functions import Length
from django.test import SimpleTestCase, TestCase, TransactionTestCase

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.models import AuthUser
from django_spire.history.activity.context import (
    activity_user,
    get_current_user,
    get_delete_activity_entries,
    set_current_user
)
from django_spire.history.activity.models import Activity
from django_spire.history.activity.signals import (
    connect_activity_signals,
    create_activity_on_m2m_change
)

from test_project.app.task.models import Task

if TYPE_CHECKING:
    from collections.abc import Callable


def run_threads(targets: list[Callable[[], None]]) -> list[Exception]:
    errors = []

    def wrap(target: Callable[[], None]) -> None:
        try:
            target()
        except Exception as error:
            errors.append(error)
        finally:
            connection.close()

    threads = [threading.Thread(target=wrap, args=(target,)) for target in targets]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return errors


class RobustnessTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='robustuser',
            password='testpass',  # noqa: S106
            first_name='Robust',
            last_name='User',
        )

    def tearDown(self) -> None:
        set_current_user(None)


class TestAsyncContextPropagation(SimpleTestCase):
    def tearDown(self) -> None:
        set_current_user(None)

    def test_async_task_inherits_outer_user(self) -> None:
        user = User(pk=1, first_name='Async', last_name='User')
        set_current_user(user)

        async def read_user() -> User | None:
            return get_current_user()

        assert asyncio.run(read_user()) == user

    def test_activity_user_inside_coroutine_does_not_leak_out(self) -> None:
        user = User(pk=1, first_name='Async', last_name='User')

        async def scoped_read() -> User | None:
            with activity_user(user):
                return get_current_user()

        assert asyncio.run(scoped_read()) == user
        assert get_current_user() is None

    def test_gathered_tasks_are_isolated(self) -> None:
        user_one = User(pk=1, first_name='One', last_name='User')
        user_two = User(pk=2, first_name='Two', last_name='User')

        async def scoped_read(user: User) -> User | None:
            with activity_user(user):
                await asyncio.sleep(0)
                return get_current_user()

        async def run_both() -> list[User | None]:
            reads = [scoped_read(user_one), scoped_read(user_two)]
            return await asyncio.gather(*reads)

        assert asyncio.run(run_both()) == [user_one, user_two]
        assert get_current_user() is None


class TestTransactionalConsistency(RobustnessTestCase):
    def test_rollback_discards_activity_with_the_write(self) -> None:
        set_current_user(self.user)
        message = 'forced rollback'

        def create_then_fail() -> None:
            Task.objects.create(name='One')

            assert Activity.objects.count() == 1

            raise RuntimeError(message)

        with pytest.raises(RuntimeError, match=message), transaction.atomic():
            create_then_fail()

        assert Task.objects.count() == 0
        assert Activity.objects.count() == 0

    def test_savepoint_rollback_keeps_outer_activity(self) -> None:
        set_current_user(self.user)
        message = 'inner rollback'

        task = Task.objects.create(name='Outer')

        def create_then_fail() -> None:
            Task.objects.create(name='Inner')
            raise RuntimeError(message)

        with pytest.raises(RuntimeError, match=message), transaction.atomic():
            create_then_fail()

        assert Task.objects.count() == 1
        assert Activity.objects.count() == 1
        assert Activity.objects.first().object_id == task.pk

    def test_activity_failure_aborts_the_write_inside_atomic(self) -> None:
        set_current_user(self.user)
        message = 'activity insert failed'

        target = 'django_spire.history.activity.signals.add_activity'

        with (
            pytest.raises(RuntimeError, match=message),
            transaction.atomic(),
            patch(target, side_effect=RuntimeError(message)),
        ):
            Task.objects.create(name='One')

        assert Task.objects.count() == 0
        assert Activity.objects.count() == 0

    def test_queryset_delete_audit_failure_rolls_back_the_delete(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)
        message = 'delete audit insert failed'

        target = 'django_spire.history.activity.utils.add_bulk_delete_activity'

        with (
            pytest.raises(RuntimeError, match=message),
            patch(target, side_effect=RuntimeError(message)),
        ):
            Task.objects.filter(pk=task.pk).delete()

        assert Task.objects.filter(pk=task.pk).count() == 1
        assert Activity.objects.filter(verb='deleted').count() == 0

    def test_update_audit_failure_rolls_back_the_update(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)
        message = 'update audit insert failed'

        target = 'django_spire.history.activity.utils.add_bulk_activity'

        with (
            pytest.raises(RuntimeError, match=message),
            patch(target, side_effect=RuntimeError(message)),
        ):
            Task.objects.filter(pk=task.pk).update(description='Changed')

        task.refresh_from_db()

        assert task.description == ''
        assert Activity.objects.filter(verb='updated').count() == 0


class TestFailedOperations(RobustnessTestCase):
    def test_failed_insert_logs_nothing(self) -> None:
        set_current_user(self.user)

        with pytest.raises(IntegrityError), transaction.atomic():
            Task.objects.create(name=None)

        assert Activity.objects.count() == 0

    def test_failed_queryset_delete_resets_collection_state(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)
        message = 'delete failed'

        with (
            pytest.raises(RuntimeError, match=message),
            transaction.atomic(),
            patch.object(QuerySet, 'delete', side_effect=RuntimeError(message)),
        ):
            Task.objects.all().delete()

        assert get_delete_activity_entries() is None
        assert Activity.objects.filter(verb='deleted').count() == 0

        task.delete()

        assert Activity.objects.filter(verb='deleted').count() == 1

    def test_failed_bulk_update_resets_guard_flag(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)
        message = 'bulk update failed'

        task.name = 'Renamed'

        with (
            pytest.raises(RuntimeError, match=message),
            transaction.atomic(),
            patch.object(QuerySet, 'bulk_update', side_effect=RuntimeError(message)),
        ):
            Task.objects.bulk_update([task], ['name'])

        assert Activity.objects.filter(verb='updated').count() == 0

        Task.objects.update(description='Changed')

        assert Activity.objects.filter(verb='updated').count() == 1

    def test_set_deleted_retry_after_failed_save_logs_deleted_once(self) -> None:
        set_current_user(self.user)

        task = Task.objects.create(name='One')
        task.name = None

        with pytest.raises(IntegrityError), transaction.atomic():
            task.set_deleted()

        task.name = 'One'
        task.set_deleted()

        assert Activity.objects.filter(verb='deleted', object_id=task.pk).count() == 1

    def test_save_after_failed_set_deleted_does_not_log_stale_deleted(self) -> None:
        set_current_user(self.user)

        task = Task.objects.create(name='One')
        task.name = None

        with pytest.raises(IntegrityError), transaction.atomic():
            task.set_deleted()

        task.name = 'One'
        task.is_deleted = False
        task.save()

        assert Activity.objects.filter(verb='deleted', object_id=task.pk).count() == 0
        assert Activity.objects.filter(verb='updated', object_id=task.pk).count() == 1


class TestActorBulkDeletion(TestCase):
    def tearDown(self) -> None:
        set_current_user(None)

    def test_bulk_delete_including_actor_skips_activity_with_warning(self) -> None:
        actor = AuthUser.objects.create_user(
            username='actor',
            first_name='Acting',
            last_name='User',
        )
        other = AuthUser.objects.create_user(
            username='other',
            first_name='Other',
            last_name='User',
        )
        target_pks = [actor.pk, other.pk]

        set_current_user(actor)

        with self.assertLogs('django_spire.history.querysets', level='WARNING') as logs:
            AuthUser.objects.filter(pk__in=target_pks).delete()

        assert AuthUser.objects.filter(pk__in=target_pks).count() == 0
        assert Activity.objects.filter(verb='deleted').count() == 0
        assert 'acting user was removed' in logs.output[0]

    def test_bulk_delete_excluding_actor_still_logs(self) -> None:
        actor = AuthUser.objects.create_user(
            username='actor',
            first_name='Acting',
            last_name='User',
        )
        other = AuthUser.objects.create_user(
            username='other',
            first_name='Other',
            last_name='User',
        )
        other_pk = other.pk

        set_current_user(actor)

        AuthUser.objects.filter(pk=other_pk).delete()

        activities = Activity.objects.filter(verb='deleted', object_id=other_pk)

        assert activities.count() == 1
        assert activities.first().user == actor


class TestSignalConnectionIdempotency(RobustnessTestCase):
    def test_reconnecting_signals_does_not_duplicate_activities(self) -> None:
        connect_activity_signals()
        connect_activity_signals()

        set_current_user(self.user)

        Task.objects.create(name='One')

        assert Activity.objects.filter(verb='created').count() == 1


class TestQuerySetEdgeBehavior(RobustnessTestCase):
    def test_sliced_update_raises_the_update_error_without_activity(self) -> None:
        Task.objects.create(name='One')

        set_current_user(self.user)

        with pytest.raises(TypeError, match='Cannot update'):
            Task.objects.all()[:1].update(description='Changed')

        assert Activity.objects.count() == 0

    def test_empty_update_kwargs_logs_nothing(self) -> None:
        Task.objects.create(name='One')

        set_current_user(self.user)

        updated_count = Task.objects.update()

        assert updated_count == 0
        assert Activity.objects.count() == 0

    def test_update_with_f_expression_logs_updated(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        Task.objects.filter(pk=task.pk).update(description=F('name'))

        assert Activity.objects.filter(verb='updated').count() == 1

    def test_annotated_queryset_update_logs_updated(self) -> None:
        Task.objects.create(name='One')

        set_current_user(self.user)

        annotated = Task.objects.annotate(name_length=Length('name'))
        annotated.filter(name_length=3).update(description='Changed')

        assert Activity.objects.filter(verb='updated').count() == 1

    def test_select_for_update_inside_atomic_logs_updated(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        with transaction.atomic():
            Task.objects.select_for_update().filter(pk=task.pk).update(description='Changed')

        assert Activity.objects.filter(verb='updated').count() == 1

    def test_empty_bulk_operations_log_nothing(self) -> None:
        set_current_user(self.user)

        Task.objects.bulk_create([])
        Task.objects.bulk_update([], ['name'])
        Task.objects.filter(name='Missing').delete()

        assert Activity.objects.count() == 0

    def test_bulk_create_with_batch_size_logs_every_row(self) -> None:
        set_current_user(self.user)

        tasks = [Task(name='One'), Task(name='Two'), Task(name='Three')]
        Task.objects.bulk_create(tasks, batch_size=1)

        assert Activity.objects.filter(verb='created').count() == 3

    def test_actor_falls_back_to_username_when_name_is_blank(self) -> None:
        blank_user = User.objects.create_user(username='serviceaccount')
        set_current_user(blank_user)

        task = Task.objects.create(name='One')
        activity = Activity.objects.get(object_id=task.pk)

        assert activity.information.startswith('serviceaccount created')

    def test_quotes_and_unicode_in_str_are_preserved(self) -> None:
        set_current_user(self.user)

        name = '"quoted" \N{GREEK SMALL LETTER ALPHA} name'
        task = Task.objects.create(name=name)
        activity = Activity.objects.get(object_id=task.pk)

        assert name in activity.information


class TestM2mEdgeBehavior(TestCase):
    def setUp(self) -> None:
        self.auth_user = AuthUser.objects.create_user(
            username='m2medge',
            password='testpass',  # noqa: S106
            first_name='Edge',
            last_name='User',
        )
        self.group = AuthGroup.objects.create(name='Editors')

    def tearDown(self) -> None:
        set_current_user(None)

    def test_add_by_pk_logs_added(self) -> None:
        set_current_user(self.auth_user)

        self.auth_user.groups.add(self.group.pk)

        assert Activity.objects.filter(verb='added').count() == 1

    def test_failed_clear_then_successful_clear_logs_current_count(self) -> None:
        other_user = AuthUser.objects.create_user(username='m2mother')
        self.group.user_set.set([self.auth_user, other_user])

        set_current_user(self.auth_user)
        message = 'clear failed'

        with (
            pytest.raises(RuntimeError, match=message),
            transaction.atomic(),
            patch.object(QuerySet, 'delete', side_effect=RuntimeError(message)),
        ):
            self.group.user_set.clear()

        assert Activity.objects.filter(verb='removed').count() == 0
        assert self.group.user_set.count() == 2

        self.group.user_set.clear()

        removed_activities = Activity.objects.filter(verb='removed')

        assert removed_activities.count() == 1
        assert 'removed 2 users from' in removed_activities.first().information

    def test_post_clear_without_captured_state_logs_nothing(self) -> None:
        set_current_user(self.auth_user)

        create_activity_on_m2m_change(
            sender=User.groups.through,
            instance=self.group,
            action='post_clear',
            model=User,
            pk_set=None,
        )

        assert Activity.objects.count() == 0


class TestThreadContextIsolation(TransactionTestCase):
    def tearDown(self) -> None:
        set_current_user(None)

    def test_new_thread_does_not_inherit_user(self) -> None:
        user = User.objects.create_user(username='threadmain', first_name='T', last_name='M')
        set_current_user(user)

        errors = run_threads([lambda: Task.objects.create(name='Thread Task')])

        assert errors == []
        assert Task.objects.count() == 1
        assert Activity.objects.count() == 0

    def test_threads_attribute_their_own_users(self) -> None:
        user_one = User.objects.create_user(username='threadone', first_name='One', last_name='U')
        user_two = User.objects.create_user(username='threadtwo', first_name='Two', last_name='U')
        barrier = threading.Barrier(2, timeout=10)

        def create_as(user: User, name: str) -> Callable[[], None]:
            def target() -> None:
                barrier.wait()

                with activity_user(user):
                    Task.objects.create(name=name)

            return target

        targets = [create_as(user_one, 'One'), create_as(user_two, 'Two')]
        errors = run_threads(targets)

        assert errors == []

        activity_one = Activity.objects.get(information__contains='"One"')
        activity_two = Activity.objects.get(information__contains='"Two"')

        assert activity_one.user == user_one
        assert activity_two.user == user_two

    def test_pooled_thread_does_not_leak_user_between_tasks(self) -> None:
        user = User.objects.create_user(username='pooluser', first_name='Pool', last_name='U')

        def attributed_work() -> None:
            with activity_user(user):
                Task.objects.create(name='Attributed')

        def unattributed_work() -> None:
            Task.objects.create(name='Unattributed')

        def close_worker_connection() -> None:
            connection.close()

        with ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(attributed_work).result()
            pool.submit(unattributed_work).result()
            pool.submit(close_worker_connection).result()

        assert Activity.objects.count() == 1
        assert 'Attributed' in Activity.objects.first().information


class TestConcurrentOperations(TransactionTestCase):
    def tearDown(self) -> None:
        set_current_user(None)

    def test_concurrent_updates_on_disjoint_rows_log_independently(self) -> None:
        user_one = User.objects.create_user(username='concone', first_name='One', last_name='U')
        user_two = User.objects.create_user(username='conctwo', first_name='Two', last_name='U')
        task_one = Task.objects.create(name='One')
        task_two = Task.objects.create(name='Two')
        barrier = threading.Barrier(2, timeout=10)

        def update_as(user: User, pk: int) -> Callable[[], None]:
            def target() -> None:
                barrier.wait()

                with activity_user(user):
                    Task.objects.filter(pk=pk).update(description='Changed')

            return target

        targets = [update_as(user_one, task_one.pk), update_as(user_two, task_two.pk)]
        errors = run_threads(targets)

        assert errors == []

        activities = Activity.objects.filter(verb='updated')

        assert activities.count() == 2
        assert activities.get(object_id=task_one.pk).user == user_one
        assert activities.get(object_id=task_two.pk).user == user_two

    def test_concurrent_deletes_on_disjoint_rows_log_independently(self) -> None:
        user = User.objects.create_user(username='concdel', first_name='Del', last_name='U')
        task_one = Task.objects.create(name='One')
        task_two = Task.objects.create(name='Two')
        barrier = threading.Barrier(2, timeout=10)

        def delete_pk(pk: int) -> Callable[[], None]:
            def target() -> None:
                barrier.wait()

                with activity_user(user):
                    Task.objects.filter(pk=pk).delete()

            return target

        targets = [delete_pk(task_one.pk), delete_pk(task_two.pk)]
        errors = run_threads(targets)

        assert errors == []
        assert Task.objects.count() == 0
        assert Activity.objects.filter(verb='deleted').count() == 2
