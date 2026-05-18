import logging
import time
from concurrent.futures import ThreadPoolExecutor, Future, CancelledError

from celery import Task, states

from django_spire.celery.meta import CeleryTaskMeta

_state_update_executor = ThreadPoolExecutor(max_workers=100)


def _async_update_state(backend, task_id: str, state: str, meta: dict) -> None:
    try:
        backend.store_result(task_id, meta, state)
    except Exception as e:
        logging.exception(
            'Failed to asynchronously update Celery state for task %s: %s', task_id, e
        )


class CeleryTaskTracker:
    """Used for tracking the state of a celery task inside the running task function"""

    def __init__(self, celery_task: Task, update_interval_seconds: int = 5) -> None:
        if update_interval_seconds < 5:
            message = f'{self.__class__.__name__}: Update Interval must be at least 5 seconds'
            raise ValueError(message)

        self._celery_task = celery_task
        self._update_interval_seconds = update_interval_seconds
        self._start_time_seconds = time.time()
        self._last_update_time_seconds = 0
        self._state = states.PENDING
        self._meta = CeleryTaskMeta()
        self._additional_meta = None
        self._cumulative_progress = 0
        self._pending_future: Future | None = None

    @property
    def task(self) -> Task:
        return self._celery_task

    def _is_overdue_for_update(self) -> bool:
        if time.time() - self._last_update_time_seconds > self._update_interval_seconds:
            self._last_update_time_seconds = time.time()
            return True

        return False

    def _cancel_pending_future(self) -> None:
        if self._pending_future is not None and not self._pending_future.done():
            self._pending_future.cancel()

        self._pending_future = None

    def _flush_futures(self) -> None:
        if self._pending_future is not None:
            try:
                self._pending_future.result(timeout=self._update_interval_seconds)
            except CancelledError:
                pass
            finally:
                self._pending_future = None


    def _process_overdue_update(self) -> None:
        if self._is_overdue_for_update():
            self._update_celery_task_state()

    def _update_celery_task_state(self) -> None:
        meta_payload = {**self._meta.model_dump(), **(self._additional_meta or {})}

        if self._celery_task.request.id:
            self._cancel_pending_future()

            self._pending_future = _state_update_executor.submit(
                _async_update_state,
                self._celery_task.backend,
                self._celery_task.request.id,
                self._state,
                meta_payload,
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

        self._meta.progress = range_min + (range_max - range_min) * (current_count / target_count)
        self._process_overdue_update()

    def update_cumulative_progress(self, added_value: int, target_value: int) -> None:
        self._cumulative_progress += added_value

        self._meta.progress = self._cumulative_progress / target_value
        self._process_overdue_update()

    def set_completed(self):
        self._meta.set_completed()
        self._flush_futures()

    def set_started(self):
        self._meta.set_started()
        self.update_state(states.STARTED)

    def set_started_and_completing_soon(self):
        self._meta.set_started_and_completing_soon()
        self.update_state(states.STARTED)

