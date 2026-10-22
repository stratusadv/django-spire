from __future__ import annotations

import copy
import itertools
import threading
import time
import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, PropertyMock, patch

from celery import Celery, states
from celery.result import AsyncResult
from django.db import close_old_connections
from django.test import SimpleTestCase, TransactionTestCase
from django.utils.timezone import now

from django_spire.celery.choices import CeleryTaskSourceChoices
from django_spire.celery.manager import BaseCeleryTaskManager
from django_spire.celery.meta import derive_final_meta_key
from django_spire.celery.models import CelerySchedulerTask, CeleryTask, CeleryTaskSweep
from django_spire.celery.scheduler import CeleryScheduler, SchedulerTask, claim_schedule_slot
from django_spire.celery.sweep import claim_sweep_window
from django_spire.celery.tests.factories import create_test_celery_task
from django_spire.celery.tracker import CeleryTaskTracker

if TYPE_CHECKING:
    from collections.abc import Callable

# A real in-process broker/backend for the apply harness. The project test app
# pins CELERY_BROKER_URL='memory://', but a bare AsyncResult() resolves to the
# default app, so the harness brings its own.
_harness_app = Celery('race_harness', broker='memory://', backend='cache+memory://')

_send_log: list[dict[str, Any]] = []
_send_log_lock = threading.Lock()


class _HarnessManager(BaseCeleryTaskManager):
    task_name = 'race.harness.task'
    display_name = 'Race Harness'


def _fake_send_task(**kwargs: Any) -> SimpleNamespace:
    with _send_log_lock:
        _send_log.append(dict(kwargs))

    return SimpleNamespace(id=str(uuid.uuid4()))


def _start_gate(thread_count: int) -> Callable[[], None]:
    barrier = threading.Barrier(thread_count)

    def _go() -> None:
        barrier.wait()

    return _go


def _thread_db_guard(target: Callable[[], None]) -> None:
    try:
        target()
    finally:
        close_old_connections()


class SchedulerClaimRaceTestCase(TransactionTestCase):
    """N scheduler instances, one due slot: exactly one claim, exactly one send."""

    def setUp(self) -> None:
        super().setUp()
        with _send_log_lock:
            _send_log.clear()

    def test_single_winner(self) -> None:
        fixed_now = datetime(2026, 1, 1, 0, 0, 30, tzinfo=UTC)
        unique_name = uuid.uuid4().hex[:8]

        class _EntryScheduler(CeleryScheduler):
            tasks = [
                SchedulerTask(
                    _HarnessManager,
                    '*/5 * * * *',
                    name=f'sched-race-{unique_name}',
                    nowfun=lambda: fixed_now,
                )
            ]

        entry = _EntryScheduler.tasks[0]

        # last_sent six minutes ago: the next */5 grid slot after it is already in
        # the past, so target_slot = max(now, next_slot) = now -> due this tick.
        CelerySchedulerTask.objects.create(
            schedule_key=entry.schedule_key,
            display_name=entry.name,
            crontab=entry.crontab,
            last_sent_datetime=fixed_now - timedelta(minutes=6),
        )

        instance_count = 5
        results: list[Any] = [None] * instance_count
        errors: list[BaseException] = []
        go = _start_gate(instance_count)

        def _claim(index: int) -> None:
            go()
            results[index] = claim_schedule_slot(entry, f'instance-{index}')

        def _run(index: int) -> None:
            _thread_db_guard(lambda: _claim_guarded(index, errors, _claim))

        with patch('django_spire.celery.manager.send_task', side_effect=_fake_send_task):
            threads = [
                threading.Thread(target=_run, args=(index,)) for index in range(instance_count)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=30)

        assert not errors, errors
        winners = [task for task in results if task is not None]
        assert len(winners) == 1, f'expected exactly one winner, got {len(winners)}'
        assert winners[0].state == states.PENDING

        winner_index = next(index for index, task in enumerate(results) if task is not None)
        row = CelerySchedulerTask.objects.get(schedule_key=entry.schedule_key)
        assert row.claimed_by == f'instance-{winner_index}'

        with _send_log_lock:
            sends = list(_send_log)
        assert len(sends) == 1, f'expected exactly one send, got {len(sends)}'
        assert sends[0]['headers']['spire_display_name'] == 'Race Harness'


def _claim_guarded(index: int, errors: list[BaseException], claim: Callable[[int], None]) -> None:
    try:
        claim(index)
    except BaseException as exc:
        errors.append(exc)


class SweepWindowRaceTestCase(TransactionTestCase):
    """N sweep instances, one due window: exactly one claim."""

    def test_single_winner(self) -> None:
        key = f'sweep-race-{uuid.uuid4().hex[:8]}'
        CeleryTaskSweep.objects.create(key=key, last_swept_datetime=now() - timedelta(seconds=60))

        instance_count = 5
        results: list[bool] = [False] * instance_count
        errors: list[BaseException] = []
        go = _start_gate(instance_count)

        def _claim(index: int) -> None:
            go()
            results[index] = claim_sweep_window(key, 20, f'instance-{index}')

        def _run(index: int) -> None:
            _thread_db_guard(lambda: _claim_guarded(index, errors, _claim))

        threads = [threading.Thread(target=_run, args=(index,)) for index in range(instance_count)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)

        assert not errors, errors
        assert sum(results) == 1, f'expected exactly one winner, got {sum(results)}'
        winner_index = results.index(True)
        row = CeleryTaskSweep.objects.get(key=key)
        assert row.claimed_by == f'instance-{winner_index}'


class ConcurrentApplyRaceTestCase(TransactionTestCase):
    """N web polls racing on one task: one terminal write, monotonic progress."""

    @staticmethod
    def _async_result_for(task_id: str) -> Callable[[], AsyncResult]:
        def _async_result() -> AsyncResult:
            return AsyncResult(task_id, app=_harness_app)

        return _async_result

    def test_terminal_apply_converges_under_race(self) -> None:
        task = create_test_celery_task(state=states.STARTED)
        task._task_meta = {'progress': 0.5}
        task.save()

        _harness_app.backend.store_result(str(task.task_id), 'done', states.SUCCESS)

        instance_count = 5
        errors: list[BaseException] = []
        go = _start_gate(instance_count)

        def _poll() -> None:
            go()
            CeleryTask.objects.get(pk=task.pk).services.update_from_backend()

        with patch.object(
            CeleryTask,
            'async_result',
            new_callable=PropertyMock,
            side_effect=self._async_result_for(str(task.task_id)),
        ):

            def _run_poll() -> None:
                _poll_guarded(errors, _poll)

            threads = [
                threading.Thread(target=_thread_db_guard, args=(_run_poll,))
                for _ in range(instance_count)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=30)

        assert not errors, errors
        task.refresh_from_db()
        assert task.state == states.SUCCESS
        assert task.result == 'done'

    def test_progress_is_monotonic_under_race_and_regression(self) -> None:
        task = create_test_celery_task(state=states.STARTED)
        task._task_meta = {'progress': 0.2}
        task.save()

        def _poll() -> None:
            CeleryTask.objects.get(pk=task.pk).services.update_from_backend()

        with patch.object(
            CeleryTask,
            'async_result',
            new_callable=PropertyMock,
            side_effect=self._async_result_for(str(task.task_id)),
        ):
            _harness_app.backend.store_result(str(task.task_id), {'progress': 0.9}, states.STARTED)

            instance_count = 4
            errors: list[BaseException] = []
            go = _start_gate(instance_count)

            def _raced_poll() -> None:
                go()
                _poll()

            def _run_poll() -> None:
                _poll_guarded(errors, _raced_poll)

            threads = [
                threading.Thread(target=_thread_db_guard, args=(_run_poll,))
                for _ in range(instance_count)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=30)
            assert not errors, errors

            task.refresh_from_db()
            assert task.meta.progress == 0.9

            # a regressed meta must not move progress backwards
            _harness_app.backend.store_result(str(task.task_id), {'progress': 0.1}, states.STARTED)
            _poll()
            task.refresh_from_db()
            assert task.meta.progress == 0.9


def _poll_guarded(errors: list[BaseException], poll: Callable[[], None]) -> None:
    try:
        poll()
    except BaseException as exc:
        errors.append(exc)


class DedupeUnreadyRaceTestCase(TransactionTestCase):
    """dedupe_unready reuse: sequential contract + concurrent first-send invariants."""

    def setUp(self) -> None:
        super().setUp()
        with _send_log_lock:
            _send_log.clear()

    def test_sequential_sends_reuse_unready_row(self) -> None:
        with patch('django_spire.celery.manager.send_task', side_effect=_fake_send_task):
            manager = _HarnessDedupe()
            first = manager.send_task(source=CeleryTaskSourceChoices.USER)
            second = manager.send_task(source=CeleryTaskSourceChoices.USER)
            assert second.pk == first.pk

            with _send_log_lock:
                assert len(_send_log) == 1, f'expected one send, got {len(_send_log)}'

            CeleryTask.objects.filter(pk=first.pk).update(state=states.SUCCESS)
            third = manager.send_task(source=CeleryTaskSourceChoices.USER)
            assert third.pk != first.pk

            with _send_log_lock:
                assert len(_send_log) == 2, f'expected two sends, got {len(_send_log)}'

    def test_concurrent_first_sends_never_diverge(self) -> None:
        manager = _HarnessDedupe()
        instance_count = 4
        results: list[Any] = [None] * instance_count
        errors: list[BaseException] = []
        go = _start_gate(instance_count)

        def _send(index: int) -> None:
            go()
            results[index] = manager.send_task(source=CeleryTaskSourceChoices.USER)

        def _run(index: int) -> None:
            _thread_db_guard(lambda: _claim_guarded(index, errors, _send))

        with patch('django_spire.celery.manager.send_task', side_effect=_fake_send_task):
            threads = [
                threading.Thread(target=_run, args=(index,)) for index in range(instance_count)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=30)

        assert not errors, errors

        rows = CeleryTask.objects.filter(
            reference_key=manager.reference_key, model_key=None
        ).count()
        with _send_log_lock:
            sends = len(_send_log)
        # check-then-act is not atomic: racing first sends may each publish, but
        # rows and sends must never diverge, and no row may be duplicated-per-send
        assert sends == rows, f'sends ({sends}) and rows ({rows}) diverged'
        assert 1 <= rows <= instance_count


class _HarnessDedupe(BaseCeleryTaskManager):
    task_name = 'race.harness.task.dedupe'
    display_name = 'Race Harness Dedupe'
    dedupe_unready = True


class TrackerFlusherHandoffTestCase(SimpleTestCase):
    """Writer thread vs flusher thread: final state converges, pushes are monotonic."""

    def test_handoff_loses_nothing(self) -> None:
        task = MagicMock()
        task.request.id = 'race-flusher-task'

        pushed: list[dict[str, Any]] = []
        pushed_lock = threading.Lock()

        def _store_result(task_id: Any, meta_dict: Any, state: Any) -> None:
            with pushed_lock:
                pushed.append(
                    {'task_id': str(task_id), 'meta': copy.deepcopy(meta_dict), 'state': state}
                )

        task.backend.store_result.side_effect = _store_result

        tracker = CeleryTaskTracker(task, update_interval_seconds=5)
        tracker.set_started()
        tracker.set_cumulative_progress_target_value(200)

        errors: list[BaseException] = []

        def _writer() -> None:
            try:
                for i in range(200):
                    tracker.update_cumulative_progress(added_value=1)
                    tracker.meta.data['tick'] = i
            except BaseException as exc:
                errors.append(exc)

        writer = threading.Thread(target=_writer, daemon=True)
        writer.start()
        writer.join(timeout=30)
        assert not errors, errors
        assert not writer.is_alive()

        # let the flusher drain mid-run snapshots before finish() takes ownership
        time.sleep(0.1)

        # finish drains the last pending snapshot and writes the final meta row
        tracker.finish(states.SUCCESS)

        main_pushes = [entry for entry in pushed if entry['task_id'] == 'race-flusher-task']
        final_meta_task_id = derive_final_meta_key('race-flusher-task')
        final_pushes = [entry for entry in pushed if entry['task_id'] == final_meta_task_id]

        assert main_pushes, 'flusher never pushed'
        assert len(final_pushes) == 1, f'final meta written {len(final_pushes)} times'
        assert final_pushes[0]['state'] == states.SUCCESS

        progress_values = [
            entry['meta'].get('progress')
            for entry in main_pushes
            if entry['meta'].get('progress') is not None
        ]
        assert progress_values, 'no progress in any push'
        for earlier, later in itertools.pairwise(progress_values):
            assert later >= earlier, f'progress regressed {earlier} -> {later}'
        assert progress_values[-1] <= 1.0

        # finish() captured the last state the writer produced, even when the
        # flusher had not yet pushed it to the main row
        final_meta = final_pushes[0]['meta']
        assert final_meta['progress'] == 1.0
        assert final_meta.get('completed_time') is not None
        assert final_meta['data'].get('tick') == 199
