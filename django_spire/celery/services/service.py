from __future__ import annotations

import logging
import pickle
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from celery import states
from celery.utils.serialization import get_pickleable_exception
from django.db import transaction
from django.utils.timezone import is_naive, make_aware, now
from sqlalchemy.exc import DatabaseError, OperationalError

from django_spire.celery.meta import CeleryTaskMeta
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

# CeleryTask state -> internal metric reference (fired once per transition, on the web)
_METRIC_REFERENCES = {
    states.SUCCESS: 'celery_task_success',
    states.FAILURE: 'celery_task_failure',
    states.RETRY: 'celery_task_retry',
}

# (meta_dict, result, completed_datetime, started_datetime)
_SnapshotValues = tuple[dict, bytes, datetime | None, datetime | None]


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
        self, async_result: AsyncResult, new_state: str
    ) -> tuple[dict | None, Any, CeleryExceptionResult | None]:
        """Read whatever the backend holds for this state: meta, result, or exception."""
        if new_state == states.SUCCESS:
            return None, self._safe_result_get(async_result), None
        if new_state == states.FAILURE:
            return None, None, self._capture_exception_result(async_result)
        if new_state not in states.READY_STATES:
            return async_result.info, None, None
        return None, None, None

    # ================= CELERYTASK WRITER =================
    def update_from_backend(self) -> None:
        async_result = self.obj.async_result
        new_state = async_result.state

        if self.obj.state in states.READY_STATES:
            if new_state == states.SUCCESS and self.obj.has_no_result:
                self._capture_result_lazy(async_result)
            return

        meta_dict, result, exception_result = self._read_backend_snapshot(async_result, new_state)

        if self._apply_backend_snapshot(
            new_state, meta_dict=meta_dict, result=result, exception_result=exception_result
        ):
            self._record_terminal_metric(new_state)

    def _apply_backend_snapshot(
        self,
        state: str,
        *,
        meta_dict: dict | None = None,
        result: Any = None,
        exception_result: CeleryExceptionResult | None = None,
    ) -> bool:
        """Atomically apply a backend-derived snapshot to the CeleryTask (web = single writer).

        The worker writes only the result backend; this is the one place the CeleryTask's
        state/meta/result change. Guards with the state machine (stale and
        back-transitions are dropped) and keeps progress monotonic. Returns True when
        the transition should fire the metric (a move into SUCCESS, FAILURE, or RETRY
        from a non-terminal CeleryTask).
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
                return False

            records_metric = state in _METRIC_REFERENCES and fresh.state not in states.READY_STATES

            if state in states.READY_STATES:
                snapshot = self._apply_terminal_snapshot(
                    fresh, state, result=result, exception_result=exception_result
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
                return False

            self._save_snapshot(fresh, state, snapshot)

            return records_metric

    def _apply_terminal_snapshot(
        self,
        fresh: CeleryTask,
        state: str,
        *,
        result: Any,
        exception_result: CeleryExceptionResult | None,
    ) -> _SnapshotValues:
        # the backend result column holds the return value / ExceptionInfo, not meta
        meta = fresh.meta
        if state == states.SUCCESS:
            meta.set_completed()
            new_result = fresh._result if result is _RESULT_UNAVAILABLE else pickle.dumps(result)
        else:
            if exception_result is not None:
                error_message = exception_result.message
            else:
                error_message = 'Unknown error'
            meta.set_failed(error_message)
            new_result = pickle.dumps(exception_result)

        return meta.model_dump(), new_result, now(), fresh.started_datetime

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

    # ================= METRICS =================
    def _record_terminal_metric(self, state: str) -> None:
        reference = _METRIC_REFERENCES.get(state)
        if reference is None:
            return

        try:
            from django_spire.metric.domain.statistic.services.tracking_service import (  # noqa: PLC0415
                StatisticTrackingService,
            )

            StatisticTrackingService.track_configured(reference=reference)
        except Exception:
            logger.warning('Failed to record terminal metric %s', reference, exc_info=True)
