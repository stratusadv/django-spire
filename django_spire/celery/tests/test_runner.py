from __future__ import annotations

import uuid
from unittest.mock import patch

import pytest
from celery import states
from celery.exceptions import Retry
from celery.utils.threads import LocalStack
from django.test import TestCase

from django_spire.celery.models import CeleryTask
from django_spire.celery.runner import CeleryTaskRunner, celery_task
from django_spire.celery.tests.factories import create_test_celery_task
from django_spire.celery.tracker import CeleryTaskTracker

_RETRY_ATTEMPTS = {'count': 0}


@celery_task(display_name='Runner Test Task')
def _runner_task(self: CeleryTaskRunner, value: int) -> str:  # noqa: ARG001
    return f'ok-{value}'


@celery_task(display_name='Failing Test Task')
def _failing_task(self: CeleryTaskRunner) -> None:  # noqa: ARG001
    message = 'task boom'
    raise ValueError(message)


@celery_task(display_name='Retry Test Task')
def _retry_task(self: CeleryTaskRunner, attempts: int) -> str:  # noqa: ARG001
    _RETRY_ATTEMPTS['count'] += 1
    if _RETRY_ATTEMPTS['count'] < attempts:
        message = 'not yet'
        raise Retry(message)
    return f'retried-{_RETRY_ATTEMPTS["count"]}'


class _ClassRunner(CeleryTaskRunner):
    name = 'django_spire.celery.tests.test_runner._class_runner'

    def execute(self, value: int) -> str:
        return f'class-{value}'


class CeleryTaskRunnerEagerTestCase(TestCase):
    def test_eager_apply_returns_result_and_writes_no_celery_task(self) -> None:
        with patch.object(CeleryTaskTracker, '_FLUSH_TIMEOUT_SECONDS', 1):
            eager_result = _runner_task.apply(args=[3])

        assert eager_result.result == 'ok-3'
        assert not CeleryTask.objects.filter(task_id=uuid.UUID(str(eager_result.id))).exists()


class CeleryTaskRunnerUntrackedTestCase(TestCase):
    def test_direct_call_is_untracked(self) -> None:
        if hasattr(_runner_task._local, 'tracker'):
            delattr(_runner_task._local, 'tracker')

        result = _runner_task(3)

        assert result == 'ok-3'
        assert _runner_task.tracker is None
        assert not CeleryTask.objects.exists()


class CeleryTaskRunnerTrackedTestCase(TestCase):
    def setUp(self) -> None:
        patcher = patch.object(CeleryTaskTracker, '_FLUSH_TIMEOUT_SECONDS', 1)
        patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def _drain_tracker(task: CeleryTaskRunner) -> None:
        tracker = task.tracker
        if tracker is None:
            return

        tracker._stopped.set()
        tracker._pending_event.set()
        if tracker._flusher is not None:
            tracker._flusher.join(timeout=6)

    def test_success_run_returns_result_and_leaves_celery_task_pending(self) -> None:
        task_id = uuid.uuid4()
        celery_task = create_test_celery_task(task_id=task_id, state=states.PENDING)

        try:
            _runner_task.push_request(id=task_id, called_directly=False, hostname='test-worker')
            result = _runner_task.run(3)
            tracker = _runner_task.tracker
        finally:
            _runner_task.pop_request()
            self._drain_tracker(_runner_task)

        assert result == 'ok-3'
        assert tracker is not None
        assert tracker.meta.data['worker_hostname'] == 'test-worker'
        assert tracker.meta.progress == 1.0
        assert tracker.meta.completed_time is not None

        fresh = CeleryTask.objects.get(pk=celery_task.pk)
        assert fresh.state == states.PENDING

    def test_failure_run_raises_and_leaves_celery_task_pending(self) -> None:
        task_id = uuid.uuid4()
        celery_task = create_test_celery_task(task_id=task_id, state=states.PENDING)

        try:
            _failing_task.push_request(id=task_id, called_directly=False)
            with pytest.raises(ValueError, match='task boom'):
                _failing_task.run()
            tracker = _failing_task.tracker
        finally:
            _failing_task.pop_request()
            self._drain_tracker(_failing_task)

        assert tracker is not None
        assert tracker.meta.error == 'ValueError: task boom'
        assert tracker.meta.failed_time is not None

        fresh = CeleryTask.objects.get(pk=celery_task.pk)
        assert fresh.state == states.PENDING

    def test_retry_run_sets_retries_meta_and_writes_no_celery_task(self) -> None:
        task_id = uuid.uuid4()
        _RETRY_ATTEMPTS['count'] = 0

        try:
            _retry_task.push_request(id=task_id, called_directly=False, retries=0)
            with pytest.raises(Retry):
                _retry_task.run(2)
            tracker = _retry_task.tracker
        finally:
            _retry_task.pop_request()
            self._drain_tracker(_retry_task)

        assert tracker is not None
        assert tracker.meta.retries == 1
        assert not CeleryTask.objects.filter(task_id=task_id).exists()

    def test_class_based_runner(self) -> None:
        task_id = uuid.uuid4()
        celery_task = create_test_celery_task(task_id=task_id, state=states.PENDING)
        runner = _ClassRunner()
        runner.request_stack = LocalStack()

        try:
            runner.push_request(id=task_id, called_directly=False)
            result = runner.run(4)
        finally:
            runner.pop_request()
            self._drain_tracker(runner)

        assert result == 'class-4'
        fresh = CeleryTask.objects.get(pk=celery_task.pk)
        assert fresh.state == states.PENDING
