from __future__ import annotations

import logging
import pickle
import time

from celery import current_app, states
from django.core.management.base import BaseCommand
from django.core.management.base import CommandParser
from django.utils.timezone import now

from django_spire.celery.models import CeleryTask
from django_spire.celery.result import CeleryExceptionResult, StaleStartedError

DEFAULT_THRESHOLD_SECONDS = 600
INSPECT_TIMEOUT_SECONDS = 5

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        'Resolves stale STARTED CeleryTasks (no meta update past the threshold): '
        'syncs CeleryTasks whose backend already reached a terminal state, skips '
        'CeleryTasks still active on a worker, and marks the rest FAILURE with a '
        'StaleStarted error (worker presumed dead). Stamping is skipped entirely when no '
        'live worker answers a ping (an unacked message may still be requeued). '
        '--include-pending additionally collects stale PENDING CeleryTasks: ones whose '
        'backend is terminal are synced, the rest are skipped (never stamped, since the '
        'message may still be queued or in flight).'
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--threshold',
            type=float,
            default=DEFAULT_THRESHOLD_SECONDS,
            help=(
                'Seconds without a meta progress update before a STARTED CeleryTask is '
                f'considered stale (default: {DEFAULT_THRESHOLD_SECONDS}).'
            ),
        )
        parser.add_argument(
            '--include-pending',
            action='store_true',
            help='Also collect stale PENDING CeleryTasks (sync when the backend is terminal; '
            'never marked FAILURE).',
        )
        parser.add_argument(
            '--dry-run', action='store_true', help='Report stale CeleryTasks without updating them.'
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        threshold_seconds = options['threshold']
        include_pending = options['include_pending']
        cutoff_time = time.time() - threshold_seconds

        stale_celery_tasks = self._collect_stale_celery_tasks(cutoff_time, include_pending)
        if not stale_celery_tasks:
            self.stdout.write('No stale STARTED CeleryTasks found.')
            return

        sync_pks: list[int] = []
        skipped_pks: list[int] = []
        started_failure_candidates: list[int] = []
        pending_failure_candidates: list[int] = []
        verdict_buckets = {
            'sync': sync_pks,
            'pending': pending_failure_candidates,
            'failure': started_failure_candidates,
            'skip': skipped_pks,
        }
        for pk, celery_task in stale_celery_tasks.items():
            verdict_buckets[self._classify_stale(celery_task)].append(pk)

        for pk in pending_failure_candidates:
            logger.info(
                'Reaper: skipping stale PENDING CeleryTask %s (backend not terminal; the '
                'message may still be queued or in flight)',
                stale_celery_tasks[pk].task_id,
            )
            skipped_pks.append(pk)

        live_workers = self._live_workers() if started_failure_candidates else None
        if live_workers is not None and not live_workers:
            logger.warning(
                'Reaper: no live worker answered the ping; %d stale CeleryTask(s) will not be '
                'marked FAILURE (an unacked message may still be requeued)',
                len(started_failure_candidates),
            )

        active_task_ids = self._active_task_ids() if started_failure_candidates else None
        failed_pks: list[int] = []
        for pk in started_failure_candidates:
            if self._stamp_is_safe(stale_celery_tasks[pk], live_workers, active_task_ids):
                failed_pks.append(pk)
            else:
                skipped_pks.append(pk)

        if options['dry_run']:
            self.stdout.write(
                f'{len(sync_pks)} stale CeleryTask(s) would be synced from the backend.'
            )
            self.stdout.write(
                f'{len(skipped_pks)} stale CeleryTask(s) would be skipped (task still alive).'
            )
            self.stdout.write(f'{len(failed_pks)} stale CeleryTask(s) would be marked FAILURE.')
            return

        for pk in sync_pks:
            stale_celery_tasks[pk].services.update_from_backend()

        stamped = 0
        if failed_pks:
            stamped = CeleryTask.objects.filter(pk__in=failed_pks, state=states.STARTED).update(
                state=states.FAILURE, completed_datetime=now(), _result=self._stale_stamp()
            )

        self.stdout.write(
            self.style.SUCCESS(f'Synced {len(sync_pks)} stale CeleryTask(s) from the backend.')
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Skipped {len(skipped_pks)} stale CeleryTask(s) (task still alive).'
            )
        )
        self.stdout.write(self.style.SUCCESS(f'Marked {stamped} stale CeleryTask(s) as FAILURE.'))

    def _collect_stale_celery_tasks(
        self, cutoff_time: float, include_pending: bool
    ) -> dict[int, CeleryTask]:
        stale_states = [states.STARTED]
        if include_pending:
            stale_states.append(states.PENDING)

        stale_celery_tasks: dict[int, CeleryTask] = {}
        for celery_task in CeleryTask.objects.filter(state__in=stale_states).iterator():
            last_update_time = celery_task.meta.last_update_time
            if last_update_time is None or last_update_time < cutoff_time:
                stale_celery_tasks[celery_task.pk] = celery_task

        return stale_celery_tasks

    def _classify_stale(self, celery_task: CeleryTask) -> str:
        backend_state = self._backend_state(celery_task)
        if backend_state is None:
            # no terminal evidence from the backend; never mark FAILURE on a read failure
            return 'skip'
        if backend_state in states.READY_STATES:
            return 'sync'
        if celery_task.state == states.PENDING:
            return 'pending'
        return 'failure'

    @staticmethod
    def _stamp_is_safe(
        celery_task: CeleryTask, live_workers: set[str] | None, active_task_ids: set[str] | None
    ) -> bool:
        return (
            live_workers is not None
            and bool(live_workers)
            and active_task_ids is not None
            and str(celery_task.task_id) not in active_task_ids
        )

    @staticmethod
    def _backend_state(celery_task: CeleryTask) -> str | None:
        try:
            return celery_task.async_result.state
        except Exception:
            logger.warning(
                'Reaper: backend read failed for task %s; CeleryTask will not be marked FAILURE',
                celery_task.task_id,
                exc_info=True,
            )
            return None

    @staticmethod
    def _live_workers() -> set[str] | None:
        try:
            ping = current_app.control.inspect(timeout=INSPECT_TIMEOUT_SECONDS).ping()
        except Exception:
            logger.warning(
                'Reaper: workers unreachable via inspect; no CeleryTask will be marked FAILURE',
                exc_info=True,
            )
            return None

        live_workers: set[str] = set()
        for hostname, alive in (ping or {}).items():
            if alive:
                live_workers.add(str(hostname))

        return live_workers

    @staticmethod
    def _active_task_ids() -> set[str] | None:
        try:
            active = current_app.control.inspect(timeout=INSPECT_TIMEOUT_SECONDS).active()
        except Exception:
            logger.warning(
                'Reaper: workers unreachable via inspect; no CeleryTask will be marked FAILURE',
                exc_info=True,
            )
            return None

        task_ids: set[str] = set()
        for tasks in (active or {}).values():
            for task in tasks:
                task_id = task.get('id')
                if task_id:
                    task_ids.add(str(task_id))

        return task_ids

    @staticmethod
    def _stale_stamp() -> bytes:
        exception = StaleStartedError(
            'Task made no progress updates and no worker reports it active; worker presumed dead.'
        )
        result = CeleryExceptionResult(exc=exception, einfo_pickle=None, traceback_text=None)
        return pickle.dumps(result)
