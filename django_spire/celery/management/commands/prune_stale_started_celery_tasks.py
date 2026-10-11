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
        'StaleStarted error (worker presumed dead).'
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
            '--dry-run', action='store_true', help='Report stale CeleryTasks without updating them.'
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        threshold_seconds = options['threshold']
        cutoff_time = time.time() - threshold_seconds

        stale_celery_tasks = self._collect_stale_celery_tasks(cutoff_time)
        if not stale_celery_tasks:
            self.stdout.write('No stale STARTED CeleryTasks found.')
            return

        sync_pks: list[int] = []
        skipped_pks: list[int] = []
        failure_candidates: list[int] = []
        for pk, celery_task in stale_celery_tasks.items():
            backend_state = self._backend_state(celery_task)
            if backend_state is None:
                # no terminal evidence from the backend; never mark FAILURE on a read failure
                skipped_pks.append(pk)
            elif backend_state in states.READY_STATES:
                sync_pks.append(pk)
            else:
                failure_candidates.append(pk)

        active_task_ids = self._active_task_ids() if failure_candidates else set()
        failed_pks: list[int] = []
        for pk in failure_candidates:
            if active_task_ids is None or str(stale_celery_tasks[pk].task_id) in active_task_ids:
                skipped_pks.append(pk)
            else:
                failed_pks.append(pk)

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

        updated = 0
        if failed_pks:
            updated = CeleryTask.objects.filter(pk__in=failed_pks, state=states.STARTED).update(
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
        self.stdout.write(self.style.SUCCESS(f'Marked {updated} stale CeleryTask(s) as FAILURE.'))

    def _collect_stale_celery_tasks(self, cutoff_time: float) -> dict[int, CeleryTask]:
        stale_celery_tasks: dict[int, CeleryTask] = {}
        for celery_task in CeleryTask.objects.filter(state=states.STARTED).iterator():
            last_update_time = celery_task.meta.last_update_time
            if last_update_time is None or last_update_time < cutoff_time:
                stale_celery_tasks[celery_task.pk] = celery_task

        return stale_celery_tasks

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
