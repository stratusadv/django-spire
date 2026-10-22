from __future__ import annotations

import logging
import pickle
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from celery import current_app, states
from celery.utils.serialization import get_pickleable_exception
from django.db import transaction
from django.utils.timezone import is_naive, make_aware, now
from sqlalchemy.exc import DatabaseError, OperationalError

from django_spire.celery.meta import CeleryTaskMeta, derive_final_meta_key
from django_spire.celery.result import CeleryExceptionResult
from django_spire.celery.services.queue_service import CeleryTaskQueueService
from django_spire.celery.state_machine import CeleryTaskStateMachine
from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from celery.result import AsyncResult

    from django_spire.celery.models import CeleryTask

logger = logging.getLogger(__name__)

# Sentinel: the backend result could not be read this poll (retry on the next one).
_RESULT_UNAVAILABLE = object()

# (meta_dict, result, completed_datetime, started_datetime)
_SnapshotValues = tuple[dict, bytes, datetime | None, datetime | None]

# backend states whose native terminal write destroys the last mid-run meta; the
# final meta is read from the tracker's derived backend row instead
_FINAL_META_STATES = frozenset({states.SUCCESS, states.FAILURE, states.RETRY})

# the native tracer's task_track_started write stores {'pid', 'hostname'} as the
# result of the STARTED row; that is not tracker meta, so a mid-run dict carrying
# no known CeleryTaskMeta field is dropped
_TRACKER_META_FIELDS = frozenset(CeleryTaskMeta.model_fields)


class CeleryTaskService(BaseDjangoModelService['CeleryTask']):
    obj: CeleryTask

    queue = CeleryTaskQueueService()

    # ================= BACKEND READS =================
    def _safe_result_get(self, async_result: AsyncResult) -> Any:
        try:
            return async_result.get()
        except (OperationalError, DatabaseError):
            logger.warning(
                'Failed to capture CeleryTask result for task %s', self.obj.task_id, exc_info=True
            )
            return _RESULT_UNAVAILABLE

    def _capture_result_lazy(self, async_result: AsyncResult) -> None:
        try:
            result = async_result.get()
        except (OperationalError, DatabaseError):
            return  # retry on the next poll; the state is already terminal

        self.obj.result = result

        date_done = async_result.date_done
        if is_naive(date_done):
            date_done = make_aware(date_done, UTC)

        self.obj.completed_datetime = date_done

        if self.obj.started_datetime is None:
            self.obj.started_datetime = self.obj.queued_datetime

        self.obj.save()

    def _capture_exception_result(self, async_result: AsyncResult) -> CeleryExceptionResult:
        traceback_text = getattr(async_result, 'traceback', None)
        exception: BaseException | None = None

        try:
            async_result.get()
        except (OperationalError, DatabaseError):
            exception = None
        except Exception as caught:  # the task's own raised exception
            exception = caught

        if exception is None:
            exception = Exception('Task failed')

        try:
            einfo_pickle = pickle.dumps(get_pickleable_exception(exception))
        except Exception:
            einfo_pickle = None

        return CeleryExceptionResult(exception, einfo_pickle, traceback_text)

    def _read_backend_snapshot(
        self, async_result: AsyncResult, new_state: str, meta: dict
    ) -> tuple[dict | None, Any, CeleryExceptionResult | None]:
        """Read whatever the backend holds for this state: meta, result, or exception."""
        if new_state == states.SUCCESS:
            return None, self._safe_result_get(async_result), None
        if new_state == states.FAILURE:
            return None, None, self._capture_exception_result(async_result)
        if new_state not in states.READY_STATES:
            meta_dict = meta.get('result')
            if not isinstance(meta_dict, dict):
                logger.warning(
                    'Dropped non-dict CeleryTask backend meta %r for task %s in state %s',
                    type(meta_dict).__name__,
                    self.obj.task_id,
                    new_state,
                )
                meta_dict = None
            elif not _TRACKER_META_FIELDS.intersection(meta_dict):
                logger.debug(
                    'Dropped non-tracker CeleryTask backend meta %r for task %s in state %s',
                    sorted(meta_dict),
                    self.obj.task_id,
                    new_state,
                )
                meta_dict = None

            return meta_dict, None, None
        return None, None, None

    def _read_final_meta(self, async_result: AsyncResult) -> dict | None:
        try:
            final_meta = async_result.backend.get_task_meta(derive_final_meta_key(self.obj.task_id))
        except (OperationalError, DatabaseError):
            logger.warning(
                'Failed to read final CeleryTask meta for task %s', self.obj.task_id, exc_info=True
            )
            return None

        meta_dict = final_meta.get('result')
        if not isinstance(meta_dict, dict):
            if meta_dict is not None:
                logger.warning(
                    'Dropped non-dict final CeleryTask meta %r for task %s',
                    type(meta_dict).__name__,
                    self.obj.task_id,
                )

            return None

        return meta_dict

    @staticmethod
    def _infer_terminal_state(final_meta_dict: dict) -> str:
        if final_meta_dict.get('error') or final_meta_dict.get('failed_time'):
            return states.FAILURE
        if final_meta_dict.get('completed_time'):
            return states.SUCCESS
        return states.RETRY

    @staticmethod
    def _build_final_exception_result(final_meta_dict: dict) -> CeleryExceptionResult:
        message = final_meta_dict.get('error') or 'Unknown error'
        traceback_text = final_meta_dict.get('error_traceback')
        return CeleryExceptionResult(Exception(message), None, traceback_text)

    # ================= CELERYTASK WRITER =================
    def update_from_backend(self) -> None:
        async_result = self.obj.async_result
        meta = async_result._get_task_meta()
        new_state = meta.get('status', states.PENDING)

        if self.obj.state in states.READY_STATES:
            if new_state == states.SUCCESS and self.obj.has_no_result:
                self._capture_result_lazy(async_result)
            return

        (meta_dict, result, exception_result) = self._read_backend_snapshot(
            async_result, new_state, meta
        )

        if new_state in _FINAL_META_STATES:
            final_meta_dict = self._read_final_meta(async_result)
            if final_meta_dict is not None:
                meta_dict = final_meta_dict
        else:
            # a late mid-run flusher write can clobber the native terminal write and
            # leave the main row non-terminal; the derived final-meta row is then the
            # true terminal source, so heal the transition from it
            final_meta_dict = self._read_final_meta(async_result)
            if final_meta_dict is not None:
                new_state = self._infer_terminal_state(final_meta_dict)
                meta_dict = final_meta_dict
                if new_state == states.SUCCESS:
                    result = _RESULT_UNAVAILABLE
                elif new_state == states.FAILURE:
                    exception_result = self._build_final_exception_result(final_meta_dict)

        self._apply_backend_snapshot(
            new_state, meta_dict=meta_dict, result=result, exception_result=exception_result
        )

    def cancel(self) -> str | None:
        from django_spire.celery.models import CeleryTask  # noqa: PLC0415

        try:
            current_app.control.revoke(str(self.obj.task_id), terminate=True)
        except Exception:
            logger.warning(
                'Failed to revoke CeleryTask %s on workers', self.obj.task_id, exc_info=True
            )
            return 'Workers could not be reached to cancel the task'

        with transaction.atomic():
            fresh = CeleryTask.objects.select_for_update().get(pk=self.obj.pk)

            if not CeleryTaskStateMachine.ok(fresh.state, states.REVOKED):
                return f'Task already finished with state {fresh.state_verbose}'

            fresh.state = states.REVOKED
            fresh.completed_datetime = now()
            fresh.save()

            self.obj.state = states.REVOKED
            self.obj.completed_datetime = fresh.completed_datetime

        return None

    def _apply_backend_snapshot(
        self,
        state: str,
        *,
        meta_dict: dict | None = None,
        result: Any = None,
        exception_result: CeleryExceptionResult | None = None,
    ) -> None:
        """Atomically apply a backend-derived snapshot to the CeleryTask (web = single writer).

        The worker writes only the result backend; this is the one place the CeleryTask's
        state/meta/result change. Guards with the state machine (stale and
        back-transitions are dropped) and keeps progress monotonic.
        """
        from django_spire.celery.models import CeleryTask  # noqa: PLC0415

        with transaction.atomic():
            fresh = CeleryTask.objects.select_for_update().get(pk=self.obj.pk)

            if not CeleryTaskStateMachine.ok(fresh.state, state):
                logger.warning(
                    'Dropped stale CeleryTask state transition %s -> %s for task %s',
                    fresh.state,
                    state,
                    self.obj.task_id,
                )
                return

            if state in states.READY_STATES:
                snapshot = self._apply_terminal_snapshot(
                    fresh,
                    state,
                    result=result,
                    exception_result=exception_result,
                    meta_dict=meta_dict,
                )
            elif meta_dict:
                snapshot = self._apply_meta_snapshot(fresh, meta_dict)
            else:
                snapshot = (
                    fresh.meta.model_dump(),
                    fresh._result,
                    fresh.completed_datetime,
                    fresh.started_datetime,
                )

            if not self._row_has_changed(fresh, state, snapshot):
                return

            self._save_snapshot(fresh, state, snapshot)

    def _apply_terminal_snapshot(
        self,
        fresh: CeleryTask,
        state: str,
        *,
        result: Any,
        exception_result: CeleryExceptionResult | None,
        meta_dict: dict | None = None,
    ) -> _SnapshotValues:
        # the backend result column holds the return value / ExceptionInfo, not meta
        meta = fresh.meta
        if state == states.SUCCESS:
            meta.set_completed()
            new_result = fresh._result if result is _RESULT_UNAVAILABLE else pickle.dumps(result)
            fresh.exception_traceback = ''
        else:
            if exception_result is not None:
                error_message = exception_result.message
            else:
                error_message = 'Unknown error'
            meta.set_failed(error_message)
            new_result = pickle.dumps(exception_result)
            fresh.exception_traceback = exception_result.traceback or ''

        # merged after set_completed/set_failed so the worker-side values (final data,
        # completed_time, failed_time) win over the web-side ones
        if meta_dict:
            meta.merge(CeleryTaskMeta(**meta_dict))

        new_started = fresh.started_datetime
        if new_started is None and meta.started_datetime is not None:
            new_started = meta.started_datetime

        return meta.model_dump(), new_result, now(), new_started

    def _apply_meta_snapshot(self, fresh: CeleryTask, meta_dict: dict) -> _SnapshotValues:
        previous_progress = fresh.meta.progress or 0
        meta = fresh.meta.merge(CeleryTaskMeta(**meta_dict))
        if meta.progress is not None and previous_progress > meta.progress:
            meta.progress = previous_progress

        new_started = fresh.started_datetime
        if new_started is None and meta.started_datetime is not None:
            new_started = meta.started_datetime

        return meta.model_dump(), fresh._result, fresh.completed_datetime, new_started

    @staticmethod
    def _row_has_changed(fresh: CeleryTask, state: str, snapshot: _SnapshotValues) -> bool:
        new_meta, new_result, new_completed, new_started = snapshot
        return (
            state != fresh.state
            or new_meta != fresh._task_meta
            or new_result != fresh._result
            or new_completed != fresh.completed_datetime
            or new_started != fresh.started_datetime
        )

    def _save_snapshot(self, fresh: CeleryTask, state: str, snapshot: _SnapshotValues) -> None:
        new_meta, new_result, new_completed, new_started = snapshot

        fresh.state = state
        fresh._task_meta = new_meta
        fresh._result = new_result
        fresh.completed_datetime = new_completed
        fresh.started_datetime = new_started
        fresh.save()
        self.obj.state = state
        self.obj._task_meta = new_meta
        self.obj._result = new_result
        self.obj.completed_datetime = new_completed
        self.obj.started_datetime = new_started
        self.obj.exception_traceback = fresh.exception_traceback
