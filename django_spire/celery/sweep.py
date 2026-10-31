from __future__ import annotations

import logging
import os
import socket
import threading
import time
from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.db import close_old_connections
from django.utils.timezone import now as django_now

from django_spire.celery.models import CeleryTask, CeleryTaskSweep
from django_spire.celery.process import is_web_server_process
from django_spire.celery.services.resolver import resolve_celery_tasks
from django_spire.conf import settings as spire_settings

logger = logging.getLogger(__name__)

_THREAD_NAME = 'django-spire-celery-sweep'
_DEFAULT_SWEEP_KEY = 'default'


class _SweepState:
    thread: threading.Thread | None = None
    stop_event = threading.Event()
    start_lock = threading.Lock()


_STATE = _SweepState()


def claim_sweep_window(key: str, interval_seconds: float, claimed_by: str) -> bool:
    moment = django_now()
    window_start = moment - timedelta(seconds=interval_seconds)

    CeleryTaskSweep.objects.get_or_create(
        key=key, defaults={'last_swept_datetime': moment, 'claimed_by': claimed_by}
    )

    claimed = CeleryTaskSweep.objects.filter(key=key, last_swept_datetime__lt=window_start).update(
        last_swept_datetime=moment, claimed_by=claimed_by
    )

    return claimed == 1


def _instance_id() -> str:
    return f'{socket.gethostname()}:{os.getpid()}'


def _run_stale_task_reaper() -> None:
    try:
        call_command(
            'prune_stale_started_celery_tasks', include_pending=True, stdout=StringIO()
        )
    except Exception:
        logger.exception('Failed to run stale CeleryTask reaper')


def _reaper_due(last_reaper_run: float) -> bool:
    interval_seconds = float(
        spire_settings.DJANGO_SPIRE_CELERY_SWEEP_REAPER_INTERVAL_SECONDS or 0
    )
    if interval_seconds <= 0:
        return False

    return time.monotonic() - last_reaper_run >= interval_seconds


def _sweep_loop(key: str, interval_seconds: float, task_limit: int | None) -> None:
    claimed_by = _instance_id()
    last_reaper_run = 0.0

    logger.info('Celery task sweep started with key %s', key)

    try:
        while not _STATE.stop_event.is_set():
            try:
                claimed = claim_sweep_window(key, interval_seconds, claimed_by)
            except Exception:
                logger.exception('Failed to claim CeleryTask sweep window for key %s', key)
                claimed = False

            if claimed:
                try:
                    resolve_celery_tasks(CeleryTask.objects.by_unready(), limit=task_limit)
                except Exception:
                    logger.exception('Failed to run CeleryTask sweep for key %s', key)

                if _reaper_due(last_reaper_run):
                    last_reaper_run = time.monotonic()
                    _run_stale_task_reaper()

            close_old_connections()
            _STATE.stop_event.wait(interval_seconds)
    except Exception:
        logger.exception('Celery task sweep loop crashed for key %s', key)
    finally:
        close_old_connections()
        logger.info('Celery task sweep stopped')


def start_sweep() -> bool:
    if not spire_settings.DJANGO_SPIRE_CELERY_SWEEP_ENABLED:
        return False

    if not is_web_server_process():
        return False

    with _STATE.start_lock:
        if _STATE.thread is not None and _STATE.thread.is_alive():
            return False

        interval_seconds = float(spire_settings.DJANGO_SPIRE_CELERY_SWEEP_INTERVAL_SECONDS or 30)
        task_limit = spire_settings.DJANGO_SPIRE_CELERY_SWEEP_TASK_LIMIT or None

        _STATE.stop_event.clear()
        _STATE.thread = threading.Thread(
            target=_sweep_loop,
            args=(_DEFAULT_SWEEP_KEY, interval_seconds, task_limit),
            daemon=True,
            name=_THREAD_NAME,
        )
        _STATE.thread.start()

        return True


def stop_sweep(timeout: float = 10.0) -> None:
    _STATE.stop_event.set()

    thread = _STATE.thread
    if thread is not None and thread.is_alive():
        thread.join(timeout=timeout)

    _STATE.thread = None
    _STATE.stop_event.clear()
