from __future__ import annotations

import logging
import sys
import threading
import time
import uuid
from datetime import timedelta
from typing import TYPE_CHECKING
from unittest.mock import ANY, MagicMock, patch

import pytest
from celery import states
from django.test import override_settings
from django.utils.timezone import now

from django_spire.celery.models import CeleryTask, CeleryTaskSweep
from django_spire.celery.sweep import (
    _STATE,
    _sweep_loop,
    claim_sweep_window,
    start_sweep,
    stop_sweep,
)
from django_spire.celery.tests.factories import create_test_celery_task

if TYPE_CHECKING:
    from collections.abc import Callable

_INTERVAL_SECONDS = 30


def _unique_key(prefix: str) -> str:
    return f'{prefix}_{uuid.uuid4().hex[:8]}'


def _wait_until(condition: Callable[[], bool], timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.05)
    return condition()


@pytest.fixture(autouse=True)
def reset_sweep_state():
    yield
    stop_sweep(timeout=5)


@pytest.mark.django_db
class TestClaimSweepWindow:
    def test_missing_row_is_created_without_claim(self):
        key = _unique_key('sweep')

        assert claim_sweep_window(key, _INTERVAL_SECONDS, 'test:1') is False

        row = CeleryTaskSweep.objects.get(key=key)
        assert row.claimed_by == 'test:1'

    def test_second_claimer_within_window_loses(self):
        key = _unique_key('sweep')

        assert claim_sweep_window(key, _INTERVAL_SECONDS, 'test:1') is False
        assert claim_sweep_window(key, _INTERVAL_SECONDS, 'test:2') is False

        row = CeleryTaskSweep.objects.get(key=key)
        assert row.claimed_by == 'test:1'

    def test_stale_row_is_claimed_exactly_once(self):
        key = _unique_key('sweep')
        CeleryTaskSweep.objects.create(
            key=key, last_swept_datetime=now() - timedelta(seconds=_INTERVAL_SECONDS * 2)
        )

        assert claim_sweep_window(key, _INTERVAL_SECONDS, 'test:1') is True
        assert claim_sweep_window(key, _INTERVAL_SECONDS, 'test:2') is False

        row = CeleryTaskSweep.objects.get(key=key)
        assert row.claimed_by == 'test:1'

    @pytest.mark.django_db(transaction=True)
    def test_concurrent_claimers_produce_single_winner(self):
        key = _unique_key('sweep_race')
        CeleryTaskSweep.objects.create(
            key=key, last_swept_datetime=now() - timedelta(seconds=_INTERVAL_SECONDS * 2)
        )

        worker_count = 8
        barrier = threading.Barrier(worker_count)
        wins: list[int] = []
        wins_lock = threading.Lock()

        def worker(index: int) -> None:
            barrier.wait()
            if claim_sweep_window(key, _INTERVAL_SECONDS, f'thread:{index}'):
                with wins_lock:
                    wins.append(index)

        threads = [threading.Thread(target=worker, args=(index,)) for index in range(worker_count)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)

        assert len(wins) == 1

        row = CeleryTaskSweep.objects.get(key=key)
        assert row.claimed_by == f'thread:{wins[0]}'


@pytest.mark.django_db(transaction=True)
class TestSweepLoop:
    def test_sweep_loop_resolves_unready_task(self):
        key = _unique_key('sweep_loop')
        CeleryTaskSweep.objects.create(
            key=key, last_swept_datetime=now() - timedelta(seconds=_INTERVAL_SECONDS * 2)
        )

        celery_task = create_test_celery_task(state=states.STARTED)

        finished_result = MagicMock()
        finished_result._get_task_meta.return_value = {'status': states.SUCCESS, 'result': None}
        finished_result.get.return_value = 'swept'
        finished_result.backend.get_task_meta.return_value = {
            'status': states.PENDING,
            'result': None,
        }

        def is_success() -> bool:
            celery_task.refresh_from_db()
            return celery_task.state == states.SUCCESS

        with patch.object(CeleryTask, 'async_result', new=property(lambda _: finished_result)):
            thread = threading.Thread(target=_sweep_loop, args=(key, 0.1, None), daemon=True)
            thread.start()
            try:
                assert _wait_until(is_success)
            finally:
                _STATE.stop_event.set()
                thread.join(timeout=30)
                _STATE.stop_event.clear()

        celery_task.refresh_from_db()
        assert celery_task.result == 'swept'


@pytest.mark.django_db(transaction=True)
class TestSweepReaperWiring:
    def test_loop_runs_reaper_once_when_interval_elapsed(self):
        key = _unique_key('sweep_reaper')
        CeleryTaskSweep.objects.create(
            key=key, last_swept_datetime=now() - timedelta(seconds=_INTERVAL_SECONDS * 2)
        )

        with (
            patch('django_spire.celery.sweep.call_command') as mock_call,
            override_settings(DJANGO_SPIRE_CELERY_SWEEP_REAPER_INTERVAL_SECONDS=3600),
        ):
            thread = threading.Thread(target=_sweep_loop, args=(key, 0.1, None), daemon=True)
            thread.start()
            try:
                assert _wait_until(lambda: mock_call.call_count >= 1, timeout=10)
            finally:
                _STATE.stop_event.set()
                thread.join(timeout=30)
                _STATE.stop_event.clear()

        assert mock_call.call_count == 1
        mock_call.assert_called_once_with(
            'prune_stale_started_celery_tasks', include_pending=True, stdout=ANY
        )

    def test_loop_skips_reaper_when_interval_is_zero(self):
        key = _unique_key('sweep_reaper_off')
        CeleryTaskSweep.objects.create(
            key=key, last_swept_datetime=now() - timedelta(seconds=_INTERVAL_SECONDS * 2)
        )

        with (
            patch('django_spire.celery.sweep.call_command') as mock_call,
            patch('django_spire.celery.sweep.resolve_celery_tasks') as mock_resolve,
            override_settings(DJANGO_SPIRE_CELERY_SWEEP_REAPER_INTERVAL_SECONDS=0),
        ):
            thread = threading.Thread(target=_sweep_loop, args=(key, 0.1, None), daemon=True)
            thread.start()
            try:
                assert _wait_until(lambda: mock_resolve.call_count >= 2, timeout=10)
            finally:
                _STATE.stop_event.set()
                thread.join(timeout=30)
                _STATE.stop_event.clear()

        assert mock_call.call_count == 0


@pytest.mark.django_db
class TestSweepThread:
    def test_start_returns_false_when_disabled(self):
        assert start_sweep() is False
        assert not any(
            thread.name == 'django-spire-celery-sweep' for thread in threading.enumerate()
        )

    def test_start_returns_false_when_run_main_is_false(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv('RUN_MAIN', 'false')

        with override_settings(DJANGO_SPIRE_CELERY_SWEEP_ENABLED=True):
            assert start_sweep() is False

    def test_start_returns_false_for_management_commands(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(sys, 'argv', ['./manage.py', 'migrate'])

        with override_settings(DJANGO_SPIRE_CELERY_SWEEP_ENABLED=True):
            assert start_sweep() is False

    def test_start_returns_true_for_runserver_command(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(sys, 'argv', ['./manage.py', 'runserver'])

        with override_settings(
            DJANGO_SPIRE_CELERY_SWEEP_ENABLED=True, DJANGO_SPIRE_CELERY_SWEEP_INTERVAL_SECONDS=0.1
        ):
            assert start_sweep() is True
            stop_sweep(timeout=5)

    def test_start_is_idempotent(self, monkeypatch: pytest.MonkeyPatch):
        CeleryTaskSweep.objects.filter(key='default').delete()
        monkeypatch.setenv('DJANGO_SPIRE_CELERY_WEB_PROCESS', 'true')

        with override_settings(
            DJANGO_SPIRE_CELERY_SWEEP_ENABLED=True, DJANGO_SPIRE_CELERY_SWEEP_INTERVAL_SECONDS=0.1
        ):
            assert start_sweep() is True
            assert start_sweep() is False
            stop_sweep(timeout=5)

    def test_stop_clears_thread(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv('DJANGO_SPIRE_CELERY_WEB_PROCESS', 'true')

        with override_settings(
            DJANGO_SPIRE_CELERY_SWEEP_ENABLED=True, DJANGO_SPIRE_CELERY_SWEEP_INTERVAL_SECONDS=0.1
        ):
            assert start_sweep() is True
            stop_sweep(timeout=5)

            assert not any(
                thread.name == 'django-spire-celery-sweep' for thread in threading.enumerate()
            )


@pytest.mark.django_db
class TestSweepLoopLiveness:
    def test_loop_crash_logs_error_and_exits(self, caplog: pytest.LogCaptureFixture) -> None:
        with (
            patch('django_spire.celery.sweep.claim_sweep_window', return_value=False),
            patch.object(_STATE.stop_event, 'wait', side_effect=RuntimeError('loop boom')),
            caplog.at_level(logging.INFO, logger='django_spire.celery.sweep'),
        ):
            thread = threading.Thread(
                target=_sweep_loop, args=(_unique_key('sweep_crash'), 0.1, None), daemon=True
            )
            thread.start()
            thread.join(timeout=30)

        assert not thread.is_alive()
        messages = [record.message for record in caplog.records]
        assert any('Celery task sweep loop crashed' in message for message in messages)
        assert any('Celery task sweep stopped' in message for message in messages)

    def test_graceful_stop_does_not_log_crash(self, caplog: pytest.LogCaptureFixture) -> None:
        with (
            patch('django_spire.celery.sweep.claim_sweep_window', return_value=False),
            caplog.at_level(logging.INFO, logger='django_spire.celery.sweep'),
        ):
            thread = threading.Thread(
                target=_sweep_loop, args=(_unique_key('sweep_graceful'), 0.1, None), daemon=True
            )
            thread.start()
            time.sleep(0.25)
            _STATE.stop_event.set()
            thread.join(timeout=30)
            _STATE.stop_event.clear()

        assert not thread.is_alive()
        messages = [record.message for record in caplog.records]
        assert any('Celery task sweep stopped' in message for message in messages)
        assert not any('crashed' in message for message in messages)
