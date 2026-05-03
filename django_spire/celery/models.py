from django_spire.celery.services.service import CeleryTaskService
from typing import Any
import pickle
from datetime import timedelta
from math import ceil

from celery import states
from celery.result import AsyncResult
from django.db import models
from django.utils.timezone import now

from django_spire.celery.querysets import CeleryTaskQuerySet
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
    started_datetime = models.DateTimeField(default=now)
    completed_datetime = models.DateTimeField(null=True, blank=True)
    estimated_completion_datetime = models.DateTimeField(default=now)

    has_result = models.BooleanField(default=False)
    _result = models.BinaryField(null=True, blank=True)
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
        time_delta = self.completed_datetime - self.started_datetime
        return int(time_delta.total_seconds())

    @property
    def completion_time_verbose(self) -> str:
        return format_duration(
            amount=self.completion_time_seconds, start_unit='second', min_unit='second'
        )

    @property
    def estimated_completion_percentage(self) -> float:
        percentage = (
            self.estimated_time_seconds - self.estimated_time_remaining_seconds
        ) / self.estimated_time_seconds

        percentage = min(percentage, 1.0)

        return max(percentage, 0.0)

    @property
    def estimated_completion_percentage_of_hundred(self) -> int:
        return int(self.estimated_completion_percentage * 100)

    @property
    def estimated_time_remaining_seconds(self) -> int:
        time_delta = self.estimated_completion_datetime - now()
        return int(time_delta.total_seconds())

    @property
    def estimated_time_seconds(self) -> int:
        time_delta = self.estimated_completion_datetime - self.started_datetime
        return int(time_delta.total_seconds())

    @property
    def estimated_time_remaining_verbose(self) -> str:
        return format_duration(
            amount=self.estimated_time_remaining_seconds, start_unit='second', min_unit='minute'
        )

    @property
    def has_no_result(self) -> bool:
        return not self.has_result

    @property
    def is_estimated_complete_soon(self) -> bool:
        time_delta = self.estimated_completion_datetime - now()
        return time_delta.total_seconds() < 60.0

    @property
    def is_failed(self) -> bool:
        return self.state == states.FAILURE

    @property
    def is_successful(self) -> bool:
        return self.state == states.SUCCESS

    @property
    def is_processing(self) -> bool:
        return self.state in states.UNREADY_STATES

    @property
    def result(self) -> Any:
        if self.state == states.FAILURE and not self.send_failed:
            return None

        if self.has_no_result and not self.send_failed:
            self.services.update_result()

        if self.has_result:
            return pickle.loads(self._result)

        return None

    @result.setter
    def result(self, result) -> Any:
        self._result = pickle.dumps(result)

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
