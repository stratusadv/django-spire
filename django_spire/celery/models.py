from django_spire.celery.result import set_pickled_no_result, CeleryNoResult
import pickle
from typing import Any

from celery import states
from celery.result import AsyncResult
from django.db import models
from django.utils.timezone import now

from django_spire.celery.meta import CeleryTaskMeta
from django_spire.celery.querysets import CeleryTaskQuerySet
from django_spire.celery.services.service import CeleryTaskService
from django_spire.contrib.utils import format_duration


def _celery_state_choices() -> list:
    return [(state, state.title()) for state in states.ALL_STATES]


class CeleryTask(models.Model):
    task_id = models.UUIDField(editable=False)
    task_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)

    reference_key = models.CharField(max_length=128)
    model_key = models.CharField(max_length=128, null=True, blank=True)

    state = models.CharField(max_length=16, choices=_celery_state_choices, default=states.PENDING)

    _task_meta = models.JSONField(default=dict, null=True, blank=True)

    queued_datetime = models.DateTimeField(default=now)
    started_datetime = models.DateTimeField(null=True, blank=True)
    completed_datetime = models.DateTimeField(null=True, blank=True)

    _result = models.BinaryField(default=set_pickled_no_result)
    _result_capture_attempts = models.PositiveSmallIntegerField(default=0)

    objects = CeleryTaskQuerySet.as_manager()

    services = CeleryTaskService()

    def __str__(self) -> str:
        return f'{self.task_name}'

    @property
    def async_result(self) -> AsyncResult:
        return AsyncResult(str(self.task_id))

    @property
    def completion_time_seconds(self) -> int:
        if self.completed_datetime:
            time_delta = self.completed_datetime - self.queued_datetime
            return int(time_delta.total_seconds())
        return 0

    @property
    def completion_time_verbose(self) -> str:
        return format_duration(amount=self.completion_time_seconds)

    @property
    def estimated_progress(self) -> float | None:
        return self.meta.estimated_progress

    @property
    def estimated_progress_hundred(self) -> int:
        if self.meta.estimated_progress:
            return int(self.meta.estimated_progress * 100)

        return 0

    @property
    def estimated_progress_per_second_hundred(self) -> float:
        return self.meta.estimated_progress_per_second * 100

    @property
    def has_result(self) -> bool:
        return not isinstance(pickle.loads(self._result), CeleryNoResult)

    @property
    def has_no_result(self) -> bool:
        return not self.has_result

    @property
    def is_estimated_complete_soon(self) -> bool:
        print(f'{self.meta.estimated_remaining_seconds=}')
        if self.meta.estimated_remaining_seconds:
            return 10 > self.meta.estimated_remaining_seconds >= 0
        return False

    @property
    def is_failed(self) -> bool:
        return self.state == states.FAILURE

    @property
    def is_remaining_time_unknown(self) -> bool:
        return self.meta.estimated_remaining_seconds is None

    @property
    def is_pending(self) -> bool:
        return self.state == states.PENDING

    @property
    def is_processing(self) -> bool:
        return self.state not in states.READY_STATES and self.state not in states.EXCEPTION_STATES

    @property
    def is_successful(self) -> bool:
        return self.state == states.SUCCESS

    @property
    def meta(self) -> CeleryTaskMeta:
        if isinstance(self._task_meta, dict):
            return CeleryTaskMeta(**self._task_meta)
        return CeleryTaskMeta()

    @meta.setter
    def meta(self, value: Any) -> None:
        self._task_meta = value

    @property
    def queue_time_seconds(self) -> int:
        if self.queued_datetime and self.started_datetime:
            time_delta = self.started_datetime - self.queued_datetime
            return int(time_delta.total_seconds())
        return 1

    @property
    def remaining_time_verbose(self) -> str | None:
        if self.meta.estimated_remaining_seconds:
            return format_duration(amount=self.meta.estimated_remaining_seconds)

        return None

    @property
    def result(self) -> Any:
        if self.state == states.FAILURE and not self.send_failed:
            return None

        if self.has_no_result and not self.send_failed:
            self.services.update_result(self.async_result)

        if self.has_result:
            return pickle.loads(self._result)

        return None

    @result.setter
    def result(self, value: Any) -> Any:
        self._result = pickle.dumps(value)

    @result.deleter
    def result(self) -> Any:
        self._result = None

    @property
    def send_failed(self) -> bool:
        if self.has_result and self._result:
            result_data = pickle.loads(self._result)
            return isinstance(result_data, dict) and result_data.get('error') == 'SEND_FAILED'

        return False

    @property
    def send_error_message(self) -> str | None:
        if self.send_failed:
            result_data = pickle.loads(self._result)
            return result_data.get('message')
        return None

    @property
    def send_error_details(self) -> dict | None:
        if self.send_failed:
            result_data = pickle.loads(self._result)
            return {
                'task_name': result_data.get('task_name'),
                'args': result_data.get('args'),
                'kwargs': result_data.get('kwargs'),
                'message': result_data.get('message'),
            }
        return None

    class Meta:
        verbose_name = 'Celery Task'
        verbose_name_plural = 'Celery Tasks'
        db_table = 'django_spire_celery_task'
        ordering = ('-started_datetime',)
