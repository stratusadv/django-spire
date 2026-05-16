import threading
import time

from celery import Task, states
from sqlalchemy.ext.asyncio import AsyncResult

from django_spire.celery.meta import CeleryTaskMeta

_ESTIMATED_REMAINING_SECONDS_MULTIPLIER = 1.10



class CeleryTaskTracker:
    """Used for tracking the state of a celery task inside the running task function"""

    def __init__(self, celery_task: Task, update_interval_seconds: int = 8) -> None:
        self._celery_task = celery_task
        self._update_interval_seconds = update_interval_seconds
        self._start_time_seconds = time.time()
        self._last_update_time_seconds = time.time()
        self._state = states.STARTED
        self._meta = CeleryTaskMeta()
        self._additional_meta = None
        self._cumulative_progress = 0

    @property
    def _remaining_seconds(self) -> int:
        return self._meta.remaining_seconds

    @property
    def _progress(self) -> float:
        return self._meta.progress

    @_progress.setter
    def _progress(self, value: float) -> None:
        self._meta.progress = round(max(0.0, min(value, 1.0)), 3)
        self._update_remaining_seconds()

    @property
    def task(self) -> Task:
        return self._celery_task

    def _is_overdue_for_update(self) -> bool:
        if time.time() - self._last_update_time_seconds > self._update_interval_seconds:
            self._last_update_time_seconds = time.time()
            return True

        return False

    def _process_overdue_update(self) -> None:
        if self._is_overdue_for_update():
            self._update_celery_task_state()

    def _update_celery_task_state(self) -> None:
        self._celery_task.update_state(
            state=self._state,
            meta={
                **self._meta.model_dump(),
                **(self._additional_meta or {})
            }
        )

    def update_state(self, state: str = states.PENDING, meta: dict | None = None) -> None:
        self._state = state.upper()
        self._additional_meta = meta

        self._process_overdue_update()

    def update_count_progress(
            self, current_count: int, target_count: int, range_min: float = 0.0, range_max: float = 1.0
    ) -> None:
        if range_min < 0.0 or range_min > range_max or range_max > 1.0:
            message = 'Progress range is invalid'
            raise ValueError(message)

        self._progress = range_min + (range_max - range_min) * (current_count / target_count)
        self._process_overdue_update()

    def update_cumulative_progress(self, added_value: int, target_value: int) -> None:
        self._cumulative_progress += added_value

        self._progress = self._cumulative_progress / target_value
        self._process_overdue_update()

    def _update_remaining_seconds(self) -> None:
        elapsed_seconds = time.time() - self._start_time_seconds
        estimated_total_seconds = elapsed_seconds / self._progress
        remaining_seconds = estimated_total_seconds - elapsed_seconds

        self._meta.remaining_seconds = int(
            remaining_seconds * _ESTIMATED_REMAINING_SECONDS_MULTIPLIER
        )

    def set_completed(self):
        self._meta.remaining_seconds = 0
        self._meta.progress = 1.0
        self._update_celery_task_state()
