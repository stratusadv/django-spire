from __future__ import annotations

import uuid
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.utils.timezone import now

from django_spire.celery.manager import BaseCeleryTaskManager
from django_spire.celery.models import CelerySchedulerTask, CeleryTaskSweep
from django_spire.celery.scheduler import CeleryScheduler, SchedulerTask

_MODULE_PATH = 'django_spire.celery.tests.test_check_celery_threads'
_COMMAND_PATH = 'django_spire.celery.management.commands.check_celery_threads'


class CheckThreadsManager(BaseCeleryTaskManager):
    task_name = 'check.threads'
    display_name = 'Check Threads'

    def send_task(self, **kwargs) -> None:  # noqa: ARG002
        return None


class _MidnightScheduler(CeleryScheduler):
    tasks = [SchedulerTask(CheckThreadsManager, '0 0 * * *', name='Midnight')]


class _MinuteScheduler(CeleryScheduler):
    tasks = [SchedulerTask(CheckThreadsManager, '*/1 * * * *', name='Minute')]


_MIDNIGHT_SCHEDULER_PATH = f'{_MODULE_PATH}._MidnightScheduler'
_MINUTE_SCHEDULER_PATH = f'{_MODULE_PATH}._MinuteScheduler'
_MIDNIGHT_KEY = _MidnightScheduler.tasks[0].schedule_key
_MINUTE_KEY = _MinuteScheduler.tasks[0].schedule_key


def _unique_key(prefix: str) -> str:
    return f'{prefix}_{uuid.uuid4().hex[:8]}'


def _run_command(*args: str) -> str:
    out = StringIO()
    call_command('check_celery_threads', *args, stdout=out)

    return out.getvalue()


@pytest.mark.django_db
class TestCheckCeleryThreads:
    def test_disabled_components_are_skipped(self) -> None:
        output = _run_command()

        assert 'sweep: SKIPPED' in output
        assert 'scheduler: SKIPPED' in output

    @override_settings(DJANGO_SPIRE_CELERY_SWEEP_ENABLED=True)
    def test_fresh_sweep_row_is_ok_and_fail_passes(self) -> None:
        key = _unique_key('sweep_fresh')
        CeleryTaskSweep.objects.create(key=key)

        with patch(f'{_COMMAND_PATH}._DEFAULT_SWEEP_KEY', key):
            output = _run_command('--fail')

        assert 'sweep: OK' in output

    @override_settings(DJANGO_SPIRE_CELERY_SWEEP_ENABLED=True)
    def test_stale_sweep_row_is_stale(self) -> None:
        key = _unique_key('sweep_stale')
        CeleryTaskSweep.objects.create(key=key, last_swept_datetime=now() - timedelta(hours=1))

        with patch(f'{_COMMAND_PATH}._DEFAULT_SWEEP_KEY', key):
            output = _run_command()

        assert 'sweep: STALE' in output

    @override_settings(DJANGO_SPIRE_CELERY_SWEEP_ENABLED=True)
    def test_stale_sweep_with_fail_exits_nonzero(self) -> None:
        key = _unique_key('sweep_stale_fail')
        CeleryTaskSweep.objects.create(key=key, last_swept_datetime=now() - timedelta(hours=1))

        with (
            patch(f'{_COMMAND_PATH}._DEFAULT_SWEEP_KEY', key),
            pytest.raises(SystemExit) as exc_info,
        ):
            _run_command('--fail')

        assert exc_info.value.code == 1

    @override_settings(DJANGO_SPIRE_CELERY_SWEEP_ENABLED=True)
    def test_missing_sweep_row_is_stale(self) -> None:
        key = _unique_key('sweep_missing')

        with patch(f'{_COMMAND_PATH}._DEFAULT_SWEEP_KEY', key):
            output = _run_command()

        assert 'sweep: STALE' in output

    @override_settings(DJANGO_SPIRE_CELERY_SWEEP_ENABLED=True)
    def test_max_age_widens_sweep_grace(self) -> None:
        key = _unique_key('sweep_max_age')
        CeleryTaskSweep.objects.create(key=key, last_swept_datetime=now() - timedelta(hours=1))

        with patch(f'{_COMMAND_PATH}._DEFAULT_SWEEP_KEY', key):
            output = _run_command('--max-age', '7200')

        assert 'sweep: OK' in output

    @override_settings(
        DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED=True,
        DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES=[_MIDNIGHT_SCHEDULER_PATH],
    )
    def test_fresh_scheduler_entry_is_ok(self) -> None:
        CelerySchedulerTask.objects.create(
            schedule_key=_MIDNIGHT_KEY,
            display_name='Midnight',
            crontab='0 0 * * *',
            last_sent_datetime=now(),
        )

        output = _run_command()

        assert 'scheduler: OK' in output

    @override_settings(
        DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED=True,
        DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES=[_MINUTE_SCHEDULER_PATH],
    )
    def test_past_due_scheduler_entry_is_stale(self) -> None:
        CelerySchedulerTask.objects.create(
            schedule_key=_MINUTE_KEY,
            display_name='Minute',
            crontab='*/1 * * * *',
            last_sent_datetime=now() - timedelta(hours=48),
        )

        output = _run_command()

        assert 'scheduler: STALE' in output

    @override_settings(
        DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED=True,
        DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES=[_MINUTE_SCHEDULER_PATH],
    )
    def test_missing_scheduler_row_is_stale(self) -> None:
        output = _run_command()

        assert 'scheduler: STALE' in output

    @override_settings(
        DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED=True,
        DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES=[_MINUTE_SCHEDULER_PATH],
    )
    def test_stale_scheduler_with_fail_exits_nonzero(self) -> None:
        CelerySchedulerTask.objects.create(
            schedule_key=_MINUTE_KEY,
            display_name='Minute',
            crontab='*/1 * * * *',
            last_sent_datetime=now() - timedelta(hours=48),
        )

        with pytest.raises(SystemExit) as exc_info:
            _run_command('--fail')

        assert exc_info.value.code == 1
