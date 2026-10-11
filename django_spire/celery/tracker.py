import logging
import threading

from celery import Task, states
from pydantic import BaseModel

from django_spire.celery.meta import CeleryTaskMeta

logger = logging.getLogger(__name__)


class _TrackerSnapshot:
    def __init__(self, state: str, meta_dict: dict) -> None:
        self.state = state
        self.meta_dict = meta_dict


class CeleryTaskTracker:
    _FLUSH_TIMEOUT_SECONDS = 10

    def __init__(
        self,
        celery_task: Task,
        update_interval_seconds: int = 5,
        data_model: type[BaseModel] | None = None,
    ) -> None:
        if update_interval_seconds < 5:
            message = f'{self.__class__.__name__}: Update Interval must be at least 5 seconds'
            raise ValueError(message)

        self.meta = CeleryTaskMeta()

        self._celery_task = celery_task
        self._data_model = data_model
        self._update_interval_seconds = update_interval_seconds
        self._lock = threading.Lock()
        self._state = states.PENDING
        self._cumulative_progress = 0
        self._cumulative_target_value: int | None = None
        self._pending_snapshot: _TrackerSnapshot | None = None
        self._pending_event = threading.Event()
        self._stopped = threading.Event()
        self._flusher: threading.Thread | None = None

    @property
    def task(self) -> Task:
        return self._celery_task

    # ================= TASK AUTHOR API =================
    def set_started(self) -> None:
        with self._lock:
            self.meta.set_started()

        self.update_state(states.STARTED)

    def set_completed(self) -> None:
        # mid-run: a scheduled update (progress=1, completed_time set), never the terminal write
        with self._lock:
            self.meta.set_completed()

        self._schedule_update()

    def set_started_and_completing_soon(self) -> None:
        with self._lock:
            self.meta.set_started_and_completing_soon()

        self.update_state(states.STARTED)

    def update_state(self, state: str = states.PENDING) -> None:
        with self._lock:
            self._state = state.upper()

            if len(self._state) > 32:
                self._state = self._state[:28] + ' ...'

        self._schedule_update()

    def update_count_progress(
        self, current_count: int, target_count: int, range_min: float = 0.0, range_max: float = 1.0
    ) -> None:
        if range_min < 0.0 or range_min > range_max or range_max > 1.0:
            message = 'Progress range is invalid'
            raise ValueError(message)

        if target_count == 0:
            message = (
                f'{self.__class__.__name__}: update_count_progress target_count must be non-zero'
            )
            raise ValueError(message)

        with self._lock:
            progress = range_min + (range_max - range_min) * (current_count / target_count)
            self.meta.progress = progress

        self._schedule_update()

    def set_cumulative_progress_target_value(self, value: int) -> None:
        with self._lock:
            self._cumulative_target_value = value

    def update_cumulative_progress(self, added_value: int) -> None:
        with self._lock:
            if self._cumulative_target_value is None:
                message = f'{self.__class__.__name__}: Cumulative Progress Target Value is None'
                raise ValueError(message)

            self._cumulative_progress = min(
                self._cumulative_progress + added_value, self._cumulative_target_value
            )
            self.meta.progress = self._cumulative_progress / self._cumulative_target_value

        self._schedule_update()

    def set_data(self, **kwargs) -> None:
        with self._lock:
            self.meta.data.update(kwargs)
            self._validate_data(self.meta.data)

        self._schedule_update()

    def set_retries(self, count: int) -> None:
        with self._lock:
            self.meta.retries = count

        self._schedule_update()

    # ================= TERMINAL (runner only) =================
    def finish(self, state: str, exc: BaseException | None = None) -> None:
        with self._lock:
            if state == states.SUCCESS:
                self.meta.set_completed()
            elif state == states.FAILURE and exc is not None:
                self.meta.set_failed(f'{type(exc).__name__}: {exc}')

        # the terminal backend write is owned by the native tracer (mark_as_done /
        # mark_as_failure / mark_as_retry); just stop the mid-run flusher
        if self._flusher is not None:
            self._stop_flusher()

    # ================= INTERNAL =================
    def _validate_data(self, data: dict) -> None:
        if self._data_model is None:
            return

        self._data_model.model_validate(data)

    def _build_snapshot(self) -> _TrackerSnapshot:
        return _TrackerSnapshot(self._state, self.meta.model_dump())

    def _schedule_update(self) -> None:
        # untracked / direct calls have no task_id, so there is no backend to push to
        if self._celery_task.request.id is None:
            return

        with self._lock:
            snapshot = self._build_snapshot()
            self._pending_snapshot = snapshot

        self._ensure_flusher()
        self._pending_event.set()

    def _ensure_flusher(self) -> None:
        if self._flusher is None or not self._flusher.is_alive():
            self._stopped.clear()

            flusher_name = f'celery-task-tracker-{self._celery_task.request.id}'
            self._flusher = threading.Thread(
                target=self._flusher_loop, daemon=True, name=flusher_name
            )
            self._flusher.start()

    def _flusher_loop(self) -> None:
        while not self._stopped.is_set():
            self._pending_event.wait(timeout=self._update_interval_seconds)
            self._pending_event.clear()

            snapshot = self._take_pending_snapshot()

            if snapshot is not None:
                self._push_to_backend(snapshot)

    def _take_pending_snapshot(self) -> _TrackerSnapshot | None:
        with self._lock:
            snapshot = self._pending_snapshot
            self._pending_snapshot = None

            return snapshot

    def _stop_flusher(self) -> None:
        self._stopped.set()

        if self._flusher is not None:
            self._flusher.join(timeout=self._FLUSH_TIMEOUT_SECONDS)

            if self._flusher.is_alive():
                logger.warning(
                    'CeleryTaskTracker flusher for task %s did not stop within %s seconds',
                    self._celery_task.request.id,
                    self._FLUSH_TIMEOUT_SECONDS,
                )

    def _push_to_backend(self, snapshot: _TrackerSnapshot) -> None:
        if self._celery_task.request.id is None:
            return

        try:
            self._celery_task.backend.store_result(
                self._celery_task.request.id, snapshot.meta_dict, snapshot.state
            )
        except Exception:
            logger.exception(
                'Failed to mirror CeleryTask state for task %s to the result backend',
                self._celery_task.request.id,
            )
