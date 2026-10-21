from __future__ import annotations

import logging
import os
import re
import socket
import threading
from typing import Any, Callable

import celery.schedules
from django.db import close_old_connections
from django.db.models import Q
from django.utils.module_loading import import_string
from django.utils.timezone import now as django_now

from django_spire.celery.choices import CeleryTaskSourceChoices
from django_spire.celery.manager import BaseCeleryTaskManager
from django_spire.celery.models import CelerySchedulerTask, CeleryTask
from django_spire.celery.process import is_web_server_process
from django_spire.conf import settings as spire_settings

logger = logging.getLogger(__name__)

_THREAD_NAME = 'django-spire-celery-scheduler'


class _SchedulerState:
    thread: threading.Thread | None = None
    stop_event = threading.Event()
    start_lock = threading.Lock()


_STATE = _SchedulerState()


class SchedulerTask:
    def __init__(
        self,
        manager_class: type[BaseCeleryTaskManager],
        crontab: str,
        *,
        name: str | None = None,
        kwargs: dict[str, Any] | None = None,
        nowfun: Callable[[], Any] | None = None,
    ) -> None:
        if not isinstance(manager_class, type) or not issubclass(
            manager_class, BaseCeleryTaskManager
        ):
            message = (
                f'SchedulerTask manager_class must be a BaseCeleryTaskManager '
                f'subclass, got {manager_class!r}'
            )
            raise TypeError(message)

        fields = crontab.split()
        if len(fields) != 5:
            message = (
                'SchedulerTask crontab must have 5 fields '
                f'(minute hour day-of-month month day-of-week), got "{crontab}"'
            )
            raise ValueError(message)

        self.manager_class = manager_class
        self.crontab = crontab
        self.name = name or manager_class.display_name
        self.kwargs = dict(kwargs or {})
        self.nowfun = nowfun or django_now
        self.schedule_key: str = ''

        try:
            minute, hour, day_of_month, month_of_year, day_of_week = fields
            self.crontab_schedule = celery.schedules.crontab(
                minute, hour, day_of_week, day_of_month, month_of_year, nowfun=self.nowfun
            )
        except Exception as exc:
            message = f'Invalid crontab expression "{crontab}": {exc}'
            raise ValueError(message) from exc


class CeleryScheduler:
    tasks: list[SchedulerTask]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if getattr(cls, 'tasks', None) is None:
            message = f'{cls.__name__}.tasks is None and must be defined'
            raise ValueError(message)

        cls._validate_tasks()

    @classmethod
    def _validate_tasks(cls) -> None:
        tasks = cls.tasks

        if not isinstance(tasks, list) or not tasks:
            message = f'{cls.__name__}.tasks must be a non-empty list of SchedulerTask'
            raise ValueError(message)

        for task in tasks:
            if not isinstance(task, SchedulerTask):
                message = (
                    f'{cls.__name__}.tasks must only contain SchedulerTask instances, got {task!r}'
                )
                raise TypeError(message)

        names = [task.name for task in tasks]
        if len(names) != len(set(names)):
            message = f'{cls.__name__}.tasks contains duplicate entry names: {names}'
            raise ValueError(message)

        for task in tasks:
            task.schedule_key = f'{cls.__module__}.{cls.__qualname__}::{task.name}'

    @property
    def name_verbose(self) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', self.__class__.__name__)


def claim_schedule_slot(entry: SchedulerTask, claimed_by: str) -> CeleryTask | None:
    moment = entry.nowfun()

    schedule_row, _ = CelerySchedulerTask.objects.get_or_create(
        schedule_key=entry.schedule_key,
        defaults={
            'display_name': entry.name,
            'crontab': entry.crontab,
            'last_sent_datetime': moment,
            'claimed_by': claimed_by,
        },
    )

    if schedule_row.last_sent_datetime >= moment:
        return None

    target_slot = moment + entry.crontab_schedule.remaining_estimate(
        schedule_row.last_sent_datetime
    )

    if target_slot > moment:
        return None

    claimed = CelerySchedulerTask.objects.filter(
        schedule_key=entry.schedule_key, last_sent_datetime__lt=target_slot
    ).update(last_sent_datetime=moment, claimed_by=claimed_by)

    if claimed != 1:
        return None

    return entry.manager_class().send_task(source=CeleryTaskSourceChoices.SCHEDULED, **entry.kwargs)


def prune_unregistered_scheduler_tasks(entries: list[SchedulerTask]) -> int:
    registered_keys = {entry.schedule_key for entry in entries}

    deleted, _ = CelerySchedulerTask.objects.filter(~Q(schedule_key__in=registered_keys)).delete()

    if deleted:
        logger.info('Pruned %s unregistered CelerySchedulerTask row(s)', deleted)

    return deleted


def _instance_id() -> str:
    return f'{socket.gethostname()}:{os.getpid()}'


def _load_entries() -> list[SchedulerTask]:
    entries: list[SchedulerTask] = []

    for class_path in spire_settings.DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES or []:
        scheduler_class = import_string(class_path)
        entries.extend(scheduler_class.tasks)

    return entries


def _scheduler_loop(entries: list[SchedulerTask], tick_seconds: float) -> None:
    claimed_by = _instance_id()

    logger.info('Celery scheduler started with %s scheduled task(s)', len(entries))

    try:
        prune_unregistered_scheduler_tasks(entries)
    except Exception:
        logger.exception('Failed to prune unregistered CelerySchedulerTask rows')

    try:
        while not _STATE.stop_event.is_set():
            for entry in entries:
                try:
                    celery_task = claim_schedule_slot(entry, claimed_by)
                except Exception:
                    logger.exception('Failed to process scheduled task %s', entry.schedule_key)
                    continue

                if celery_task is None:
                    continue

                if celery_task.send_failed:
                    logger.warning(
                        'Scheduled send failed for %s: %s',
                        entry.schedule_key,
                        celery_task.send_error_message,
                    )
                else:
                    logger.info(
                        'Sent scheduled task %s (%s)', entry.schedule_key, celery_task.task_id
                    )

            _STATE.stop_event.wait(tick_seconds)
    except Exception:
        logger.exception('Celery scheduler loop crashed')
    finally:
        close_old_connections()
        logger.info('Celery scheduler stopped')


def start_scheduler() -> bool:
    if not spire_settings.DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED:
        return False

    if not spire_settings.DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES:
        return False

    if not is_web_server_process():
        return False

    with _STATE.start_lock:
        if _STATE.thread is not None and _STATE.thread.is_alive():
            return False

        entries = _load_entries()
        if not entries:
            return False

        tick_seconds = float(spire_settings.DJANGO_SPIRE_CELERY_SCHEDULER_TICK_SECONDS or 30)

        _STATE.stop_event.clear()
        _STATE.thread = threading.Thread(
            target=_scheduler_loop, args=(entries, tick_seconds), daemon=True, name=_THREAD_NAME
        )
        _STATE.thread.start()

        return True


def stop_scheduler(timeout: float = 10.0) -> None:
    _STATE.stop_event.set()

    thread = _STATE.thread
    if thread is not None and thread.is_alive():
        thread.join(timeout=timeout)

    _STATE.thread = None
    _STATE.stop_event.clear()
