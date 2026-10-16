import logging
import threading
import traceback
from typing import Any, Callable

from celery import Task, states

from django_spire.celery.meta import CeleryTaskMeta, TaskDataModel, derive_final_meta_key

logger = logging.getLogger(__name__)


class _ScheduledDataDict(dict):
    _schedule_update: Callable[[], None]

    def __setitem__(self, key: Any, value: Any) -> None:
        super().__setitem__(key, value)
        self._schedule_update()

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self._schedule_update()


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
        meta_data_model: type[TaskDataModel] | None = None,
    ) -> None:
        if update_interval_seconds < 5:
            message = f'{self.__class__.__name__}: Update Interval must be at least 5 seconds'
            raise ValueError(message)

        if meta_data_model is not None:
            meta = CeleryTaskMeta[meta_data_model](data=meta_data_model())
            meta.data._on_change = self._schedule_update
        else:
            data = _ScheduledDataDict()
            data._schedule_update = self._schedule_update
            meta = CeleryTaskMeta(data=data)

        self.meta = meta

        self._celery_task = celery_task
        self._task_id = celery_task.request.id
        self._update_interval_seconds = update_interval_seconds
        self._lock = threading.Lock()
        self._state = states.PENDING
        self._finished = False
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

    def set_retries(self, count: int) -> None:
        with self._lock:
            self.meta.retries = count

        self._schedule_update()

    # ================= TERMINAL (runner only) =================
    def finish(self, state: str, exc: BaseException | None = None) -> None:
        with self._lock:
            self._finished = True

            if state == states.SUCCESS:
                self.meta.set_completed()
            elif state == states.FAILURE and exc is not None:
                self.meta.set_failed(f'{type(exc).__name__}: {exc}')
                self.meta.error_traceback = ''.join(traceback.format_exception(exc))

            snapshot = self._build_snapshot()

        # the terminal backend write is owned by the native tracer (mark_as_done /
        # mark_as_failure / mark_as_retry); stop the mid-run flusher, then push the
        # final meta to the derived key, because the terminal write overwrites the
        # main row and would destroy it
        if self._flusher is not None:
            self._stop_flusher()

        self._push_final_meta(snapshot)

    # ================= INTERNAL =================
    def _build_snapshot(self) -> _TrackerSnapshot:
        return _TrackerSnapshot(self._state, self.meta.model_dump())

    def _schedule_update(self) -> None:
        # untracked / direct calls have no task_id, so there is no backend to push to
        if self._task_id is None:
            return

        with self._lock:
            snapshot = self._build_snapshot()
            self._pending_snapshot = snapshot

        self._ensure_flusher()
        self._pending_event.set()

    def _ensure_flusher(self) -> None:
        if self._flusher is None or not self._flusher.is_alive():
            self._stopped.clear()

            flusher_name = f'celery-task-tracker-{self._task_id}'
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
        # wake the flusher so it observes _stopped and pushes the last pending
        # snapshot instead of sleeping out the update interval
        self._pending_event.set()

        if self._flusher is not None:
            self._flusher.join(timeout=self._FLUSH_TIMEOUT_SECONDS)

            if self._flusher.is_alive():
                logger.warning(
                    'CeleryTaskTracker flusher for task %s did not stop within %s seconds',
                    self._task_id,
                    self._FLUSH_TIMEOUT_SECONDS,
                )

    def _push_to_backend(self, snapshot: _TrackerSnapshot) -> None:
        # after finish() the native tracer owns the main row, and the derived final
        # row already carries the freshest meta, so a late push would only clobber
        if self._task_id is None or self._finished:
            return

        try:
            self._celery_task.backend.store_result(
                self._task_id, snapshot.meta_dict, snapshot.state
            )
        except Exception:
            logger.exception(
                'Failed to mirror CeleryTask state for task %s to the result backend', self._task_id
            )

    def _push_final_meta(self, snapshot: _TrackerSnapshot) -> None:
        if self._task_id is None:
            return

        try:
            # always SUCCESS: sets date_done so the database backend's cleanup expires
            # the row, and keeps meta_from_decoded from exception-converting the dict
            self._celery_task.backend.store_result(
                derive_final_meta_key(self._task_id), snapshot.meta_dict, states.SUCCESS
            )
        except Exception:
            logger.exception('Failed to write final CeleryTask meta for task %s', self._task_id)
