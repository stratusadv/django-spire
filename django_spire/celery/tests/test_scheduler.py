from __future__ import annotations

import logging
import sys
import threading
import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from django.test import override_settings
from django.utils.module_loading import import_string

from django_spire.celery.choices import CeleryTaskSourceChoices
from django_spire.celery.manager import BaseCeleryTaskManager
from django_spire.celery.models import CelerySchedulerTask
from django_spire.celery.scheduler import (
    CeleryScheduler,
    SchedulerTask,
    _STATE,
    _scheduler_loop,
    claim_schedule_slot,
    prune_unregistered_scheduler_tasks,
    start_scheduler,
    stop_scheduler,
)
from test_project.app.celery.celery.managers import (
    ConvertFilesToModelObjectsCeleryTaskManager,
    ProcessReadyNotificationsCeleryTaskManager,
)
from test_project.app.celery.scheduler import TestProjectScheduler

if TYPE_CHECKING:
    from collections.abc import Callable

_BASE_TIME = datetime(2026, 1, 1, 23, 59, 30, tzinfo=UTC)
_MODULE_PATH = 'django_spire.celery.tests.test_scheduler'


class FakeManager(BaseCeleryTaskManager):
    task_name = 'fake.task'
    display_name = 'Fake Task'

    send_calls: list[dict] = []

    def send_task(self, **kwargs) -> None:
        self.send_calls.append(kwargs)


_LOOP_STATE = {'t': _BASE_TIME, 'calls': 0}


def _loop_nowfun() -> datetime:
    _LOOP_STATE['calls'] += 1

    if _LOOP_STATE['calls'] <= 1:
        return _LOOP_STATE['t']

    return _LOOP_STATE['t'] + timedelta(hours=1)


class _IdempotentScheduler(CeleryScheduler):
    tasks = [SchedulerTask(FakeManager, '0 0 * * *', name='Idempotent Task', nowfun=_loop_nowfun)]


class _LoopScheduler(CeleryScheduler):
    tasks = [SchedulerTask(FakeManager, '0 0 * * *', name='Loop Task', nowfun=_loop_nowfun)]


class _StopScheduler(CeleryScheduler):
    tasks = [SchedulerTask(FakeManager, '0 0 * * *', name='Stop Task', nowfun=_loop_nowfun)]


_IDEMPOTENT_SCHEDULER_PATH = f'{_MODULE_PATH}._IdempotentScheduler'
_LOOP_SCHEDULER_PATH = f'{_MODULE_PATH}._LoopScheduler'
_STOP_SCHEDULER_PATH = f'{_MODULE_PATH}._StopScheduler'
_IDEMPOTENT_ROW_KEY = _IdempotentScheduler.tasks[0].schedule_key
_LOOP_ROW_KEY = _LoopScheduler.tasks[0].schedule_key


def _make_entry(state: dict, crontab: str = '0 0 * * *') -> SchedulerTask:
    unique_name = uuid.uuid4().hex[:8]

    class Scheduler(CeleryScheduler):
        tasks = [SchedulerTask(FakeManager, crontab, name=unique_name, nowfun=lambda: state['t'])]

    return Scheduler.tasks[0]


def _wait_until(condition: Callable[[], bool], timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.05)
    return condition()


@pytest.fixture(autouse=True)
def reset_scheduler_state():
    FakeManager.send_calls = []
    _LOOP_STATE['t'] = _BASE_TIME
    _LOOP_STATE['calls'] = 0
    yield
    FakeManager.send_calls = []
    stop_scheduler(timeout=5)


class TestSchedulerTask:
    def test_invalid_crontab_field_count_raises(self):
        with pytest.raises(ValueError, match='must have 5 fields'):
            SchedulerTask(FakeManager, 'bad cron')

    def test_invalid_crontab_value_raises(self):
        with pytest.raises(ValueError, match='Invalid crontab expression'):
            SchedulerTask(FakeManager, '61 * * * *')

    def test_manager_must_be_base_celery_task_manager_subclass(self):
        with pytest.raises(TypeError):
            SchedulerTask(object, '0 0 * * *')  # type: ignore[arg-type]

    def test_name_defaults_to_manager_display_name(self):
        entry = SchedulerTask(FakeManager, '0 0 * * *')
        assert entry.name == 'Fake Task'

    def test_name_override(self):
        entry = SchedulerTask(FakeManager, '0 0 * * *', name='Custom')
        assert entry.name == 'Custom'

    def test_kwargs_are_copied(self):
        source = {'length': 3}
        entry = SchedulerTask(FakeManager, '0 0 * * *', kwargs=source)
        source['length'] = 99
        assert entry.kwargs == {'length': 3}


class TestCeleryScheduler:
    def test_missing_tasks_raises(self):
        with pytest.raises(ValueError, match='tasks is None and must be defined'):

            class Scheduler(CeleryScheduler):
                pass

    def test_empty_tasks_raises(self):
        with pytest.raises(ValueError, match='must be a non-empty list'):

            class Scheduler(CeleryScheduler):
                tasks = []

    def test_non_scheduler_task_entry_raises(self):
        with pytest.raises(TypeError):

            class Scheduler(CeleryScheduler):
                tasks = ['not an entry']

    def test_duplicate_names_raise(self):
        with pytest.raises(ValueError, match='duplicate entry names'):

            class Scheduler(CeleryScheduler):
                tasks = [
                    SchedulerTask(FakeManager, '0 0 * * *'),
                    SchedulerTask(FakeManager, '30 0 * * *'),
                ]

    def test_schedule_keys_are_stamped_and_unique(self):
        class Scheduler(CeleryScheduler):
            tasks = [
                SchedulerTask(FakeManager, '0 0 * * *', name='One'),
                SchedulerTask(FakeManager, '30 0 * * *', name='Two'),
            ]

        keys = [task.schedule_key for task in Scheduler.tasks]
        assert keys[0] == f'{Scheduler.__module__}.{Scheduler.__qualname__}::One'
        assert len(set(keys)) == 2

    def test_name_verbose(self):
        class MyTestScheduler(CeleryScheduler):
            tasks = [SchedulerTask(FakeManager, '0 0 * * *')]

        assert MyTestScheduler().name_verbose == 'My Test Scheduler'


@pytest.mark.django_db
class TestClaimScheduleSlot:
    def test_first_run_does_not_send_retroactively(self):
        state = {'t': _BASE_TIME}
        entry = _make_entry(state)

        CelerySchedulerTask.objects.create(
            schedule_key=entry.schedule_key,
            display_name=entry.name,
            crontab=entry.crontab,
            last_sent_datetime=_BASE_TIME - timedelta(minutes=10),
        )

        assert claim_schedule_slot(entry, 'test:1') is None
        assert FakeManager.send_calls == []

    def test_due_slot_sends_exactly_once(self):
        state = {'t': _BASE_TIME}
        entry = _make_entry(state)

        CelerySchedulerTask.objects.create(
            schedule_key=entry.schedule_key,
            display_name=entry.name,
            crontab=entry.crontab,
            last_sent_datetime=_BASE_TIME - timedelta(minutes=10),
        )

        state['t'] = _BASE_TIME + timedelta(seconds=60)
        claim_schedule_slot(entry, 'test:1')

        assert len(FakeManager.send_calls) == 1
        assert FakeManager.send_calls[0]['source'] == CeleryTaskSourceChoices.SCHEDULED

        row = CelerySchedulerTask.objects.get(schedule_key=entry.schedule_key)
        assert row.last_sent_datetime == _BASE_TIME + timedelta(seconds=60)
        assert row.claimed_by == 'test:1'

        assert claim_schedule_slot(entry, 'test:2') is None
        assert len(FakeManager.send_calls) == 1

    def test_row_is_created_when_missing(self):
        state = {'t': _BASE_TIME}
        entry = _make_entry(state)

        assert CelerySchedulerTask.objects.filter(schedule_key=entry.schedule_key).count() == 0
        claim_schedule_slot(entry, 'test:1')

        row = CelerySchedulerTask.objects.get(schedule_key=entry.schedule_key)
        assert row.last_sent_datetime == _BASE_TIME
        assert row.crontab == '0 0 * * *'
        assert row.claimed_by == 'test:1'

    def test_stale_last_sent_fires_at_most_once(self):
        state = {'t': _BASE_TIME}
        entry = _make_entry(state)

        CelerySchedulerTask.objects.create(
            schedule_key=entry.schedule_key,
            display_name=entry.name,
            crontab=entry.crontab,
            last_sent_datetime=_BASE_TIME - timedelta(days=3),
        )

        claim_schedule_slot(entry, 'test:1')
        assert len(FakeManager.send_calls) == 1

        claim_schedule_slot(entry, 'test:1')
        claim_schedule_slot(entry, 'test:1')
        assert len(FakeManager.send_calls) == 1

    @pytest.mark.django_db(transaction=True)
    def test_concurrent_claimers_produce_single_send(self):
        state = {'t': _BASE_TIME + timedelta(seconds=60)}
        entry = _make_entry(state)

        CelerySchedulerTask.objects.create(
            schedule_key=entry.schedule_key,
            display_name=entry.name,
            crontab=entry.crontab,
            last_sent_datetime=_BASE_TIME - timedelta(minutes=10),
        )

        worker_count = 8
        barrier = threading.Barrier(worker_count)

        def worker(index: int) -> None:
            barrier.wait()
            claim_schedule_slot(entry, f'thread:{index}')

        threads = [threading.Thread(target=worker, args=(index,)) for index in range(worker_count)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)

        assert len(FakeManager.send_calls) == 1

        row = CelerySchedulerTask.objects.get(schedule_key=entry.schedule_key)
        assert row.claimed_by in {f'thread:{index}' for index in range(worker_count)}


@pytest.mark.django_db
class TestPruneUnregisteredSchedulerTasks:
    def test_deletes_rows_without_registered_entries(self):
        state = {'t': _BASE_TIME}
        entry = _make_entry(state)

        CelerySchedulerTask.objects.create(
            schedule_key=entry.schedule_key, display_name=entry.name, crontab=entry.crontab
        )
        orphan_key = 'prune_test.Gone::Old Task'
        CelerySchedulerTask.objects.create(
            schedule_key=orphan_key, display_name='Old Task', crontab='0 0 * * *'
        )

        deleted = prune_unregistered_scheduler_tasks([entry])

        assert deleted == 1
        assert CelerySchedulerTask.objects.filter(schedule_key=orphan_key).count() == 0
        assert CelerySchedulerTask.objects.filter(schedule_key=entry.schedule_key).count() == 1

    def test_keeps_rows_when_every_entry_is_registered(self):
        state = {'t': _BASE_TIME}
        entry_one = _make_entry(state)
        entry_two = _make_entry(state)

        for entry in (entry_one, entry_two):
            CelerySchedulerTask.objects.create(
                schedule_key=entry.schedule_key, display_name=entry.name, crontab=entry.crontab
            )

        deleted = prune_unregistered_scheduler_tasks([entry_one, entry_two])

        assert deleted == 0
        assert CelerySchedulerTask.objects.count() == 2

    def test_deletes_all_rows_when_no_entries_remain(self):
        CelerySchedulerTask.objects.create(
            schedule_key='prune_test.GoneOne::Old One', display_name='Old One', crontab='0 0 * * *'
        )
        CelerySchedulerTask.objects.create(
            schedule_key='prune_test.GoneTwo::Old Two', display_name='Old Two', crontab='0 0 * * *'
        )

        deleted = prune_unregistered_scheduler_tasks([])

        assert deleted == 2
        assert CelerySchedulerTask.objects.count() == 0


@pytest.mark.django_db
class TestSchedulerThread:
    def test_start_returns_false_when_disabled(self):
        assert start_scheduler() is False
        assert not any(
            thread.name == 'django-spire-celery-scheduler' for thread in threading.enumerate()
        )

    def test_start_returns_false_without_classes(self):
        with override_settings(
            DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED=True, DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES=[]
        ):
            assert start_scheduler() is False

    def test_start_returns_false_when_run_main_is_false(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv('RUN_MAIN', 'false')

        with override_settings(
            DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED=True,
            DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES=[_LOOP_SCHEDULER_PATH],
        ):
            assert start_scheduler() is False

    def test_start_returns_false_for_management_commands(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(sys, 'argv', ['./manage.py', 'migrate'])

        with override_settings(
            DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED=True,
            DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES=[_LOOP_SCHEDULER_PATH],
        ):
            assert start_scheduler() is False

    def test_start_returns_true_for_runserver_command(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(sys, 'argv', ['./manage.py', 'runserver'])

        with override_settings(
            DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED=True,
            DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES=[_STOP_SCHEDULER_PATH],
            DJANGO_SPIRE_CELERY_SCHEDULER_TICK_SECONDS=0.1,
        ):
            assert start_scheduler() is True
            stop_scheduler(timeout=5)

    def test_start_returns_true_for_wsgi_entry_point(self, monkeypatch: pytest.MonkeyPatch):
        gunicorn_argv = ['/usr/local/bin/gunicorn', 'test_project.wsgi:application']
        monkeypatch.setattr(sys, 'argv', gunicorn_argv)

        with override_settings(
            DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED=True,
            DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES=[_STOP_SCHEDULER_PATH],
            DJANGO_SPIRE_CELERY_SCHEDULER_TICK_SECONDS=0.1,
        ):
            assert start_scheduler() is True
            stop_scheduler(timeout=5)

    def test_start_is_idempotent(self):
        CelerySchedulerTask.objects.filter(schedule_key=_IDEMPOTENT_ROW_KEY).delete()

        with override_settings(
            DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED=True,
            DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES=[_IDEMPOTENT_SCHEDULER_PATH],
            DJANGO_SPIRE_CELERY_SCHEDULER_TICK_SECONDS=0.1,
        ):
            assert start_scheduler() is True
            assert start_scheduler() is False
            stop_scheduler(timeout=5)

    @pytest.mark.django_db(transaction=True)
    def test_scheduler_loop_sends_due_slot_once(self):
        CelerySchedulerTask.objects.filter(schedule_key=_LOOP_ROW_KEY).delete()

        with override_settings(
            DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED=True,
            DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES=[_LOOP_SCHEDULER_PATH],
            DJANGO_SPIRE_CELERY_SCHEDULER_TICK_SECONDS=0.1,
        ):
            assert start_scheduler() is True
            try:
                assert _wait_until(lambda: len(FakeManager.send_calls) >= 1)

                time.sleep(0.3)
                assert len(FakeManager.send_calls) == 1

                row = CelerySchedulerTask.objects.get(schedule_key=_LOOP_ROW_KEY)
                assert row.last_sent_datetime == _BASE_TIME + timedelta(hours=1)
            finally:
                stop_scheduler(timeout=5)

    def test_stop_clears_thread(self):
        with override_settings(
            DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED=True,
            DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES=[_STOP_SCHEDULER_PATH],
            DJANGO_SPIRE_CELERY_SCHEDULER_TICK_SECONDS=0.1,
        ):
            assert start_scheduler() is True
            stop_scheduler(timeout=5)

            assert not any(
                thread.name == 'django-spire-celery-scheduler' for thread in threading.enumerate()
            )

    @pytest.mark.django_db(transaction=True)
    def test_loop_prunes_unregistered_rows_on_start(self):
        CelerySchedulerTask.objects.filter(schedule_key=_LOOP_ROW_KEY).delete()

        orphan_key = 'prune_test.Gone::Loop Old Task'
        CelerySchedulerTask.objects.create(
            schedule_key=orphan_key, display_name='Loop Old Task', crontab='0 0 * * *'
        )

        with override_settings(
            DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED=True,
            DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES=[_LOOP_SCHEDULER_PATH],
            DJANGO_SPIRE_CELERY_SCHEDULER_TICK_SECONDS=0.1,
        ):
            assert start_scheduler() is True
            try:
                assert _wait_until(
                    lambda: CelerySchedulerTask.objects.filter(schedule_key=orphan_key).count() == 0
                )
            finally:
                stop_scheduler(timeout=5)

            assert CelerySchedulerTask.objects.filter(schedule_key=_LOOP_ROW_KEY).count() == 1


@pytest.mark.django_db
class TestSchedulerLoopLiveness:
    def test_loop_crash_logs_error_and_exits(self, caplog: pytest.LogCaptureFixture) -> None:
        with (
            patch.object(_STATE.stop_event, 'wait', side_effect=RuntimeError('boom')),
            caplog.at_level(logging.INFO, logger='django_spire.celery.scheduler'),
        ):
            thread = threading.Thread(target=_scheduler_loop, args=([], 0.1), daemon=True)
            thread.start()
            thread.join(timeout=30)

        assert not thread.is_alive()
        messages = [record.message for record in caplog.records]
        assert any('Celery scheduler loop crashed' in message for message in messages)
        assert any('Celery scheduler stopped' in message for message in messages)

    def test_graceful_stop_does_not_log_crash(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.INFO, logger='django_spire.celery.scheduler'):
            thread = threading.Thread(target=_scheduler_loop, args=([], 0.1), daemon=True)
            thread.start()
            time.sleep(0.25)
            _STATE.stop_event.set()
            thread.join(timeout=30)
            _STATE.stop_event.clear()

        assert not thread.is_alive()
        messages = [record.message for record in caplog.records]
        assert any('Celery scheduler stopped' in message for message in messages)
        assert not any('crashed' in message for message in messages)


class TestProjectSchedulerRegistration:
    def test_test_project_scheduler_is_valid(self):
        assert len(TestProjectScheduler.tasks) == 4
        keys = [task.schedule_key for task in TestProjectScheduler.tasks]
        assert len(set(keys)) == 4
        assert TestProjectScheduler().name_verbose == 'Test Project Scheduler'

    def test_robit_jobs_are_registered(self):
        names = [task.name for task in TestProjectScheduler.tasks]
        assert 'Process Ready Notifications' in names
        assert 'Convert Files To Model Objects' in names

    def test_robit_job_crontabs_match_original(self):
        by_name = {task.name: task for task in TestProjectScheduler.tasks}
        assert by_name['Process Ready Notifications'].crontab == '0 0 * * 6'
        assert by_name['Convert Files To Model Objects'].crontab == '0 0 * * 6'

    def test_robit_managers_reference_importable_tasks(self):
        for manager in (
            ProcessReadyNotificationsCeleryTaskManager,
            ConvertFilesToModelObjectsCeleryTaskManager,
        ):
            assert callable(import_string(manager.task_name))
