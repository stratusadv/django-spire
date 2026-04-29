import pickle
from datetime import timedelta
from math import ceil

from celery import states
from celery.result import AsyncResult
from django.db import models
from django.utils.timezone import now

from django_spire.celery.querysets import CeleryTaskQuerySet

_CELERY_ESTIMATED_TIME_MULTIPLIER = 1.15


def _celery_state_choices() -> list:
    return [(state, state.title()) for state in states.ALL_STATES]


class CeleryTask(models.Model):
    task_id = models.UUIDField(editable=False)
    task_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)

    reference_key = models.CharField(max_length=128)

    state = models.CharField(max_length=16, choices=_celery_state_choices, default=states.PENDING)
    started_datetime = models.DateTimeField(default=now)
    completed_datetime = models.DateTimeField(null=True, blank=True)
    estimated_completion_datetime = models.DateTimeField(default=now)

    _result = models.BinaryField(null=True, blank=True)
    _result_capture_attempts = models.PositiveSmallIntegerField(default=0)

    objects = CeleryTaskQuerySet.as_manager()

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
        return f'{self._generate_verbose_time(self.completion_time_seconds)}'

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
        remaining_seconds = self.estimated_time_remaining_seconds
        return f'{self._generate_verbose_time(remaining_seconds, False)}'

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
    def result(self):
        return pickle.loads(self._result)

    @result.setter
    def result(self, result):
        self._result = pickle.dumps(result)

    @result.deleter
    def result(self):
        self._result = None

    @staticmethod
    def _generate_verbose_time(total_seconds: int, include_seconds: bool = True) -> str:
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = (total_seconds % 3600) % 60

        completion_time_verbose = ''

        if days:
            completion_time_verbose += f'{days} day ' if hours == 1 else f'{days} days '
        if hours:
            completion_time_verbose += f'{hours} hour ' if hours == 1 else f'{hours} hours '
        if minutes:
            completion_time_verbose += f'{minutes} minute ' if hours == 1 else f'{minutes} minutes '
        if seconds and include_seconds:
            completion_time_verbose += f'{seconds} second ' if hours == 1 else f'{seconds} seconds '

        return completion_time_verbose

    @classmethod
    def register(
            cls,
            async_result: AsyncResult,
            task_name: str,
            display_name: str,
            reference_key: str,
            estimated_completion_seconds: int | None = None,
    ) -> None:
        cls.objects.create(
            task_id=async_result.id,
            task_name=task_name[:255],
            display_name=display_name[:255],
            reference_key=reference_key[:128],
            estimated_completion_datetime=now() + timedelta(
                seconds=ceil(
                    estimated_completion_seconds * _CELERY_ESTIMATED_TIME_MULTIPLIER
                )
            )
            if estimated_completion_seconds is not None
            else now(),
        )

    def update_from_async_result_and_save(self) -> None:
        current_state = self.state

        new_state = self.async_result.state

        if self.state != states.SUCCESS and new_state == states.SUCCESS:
            try:
                self.result = self.async_result.get(timeout=10)
                self.completed_datetime = now()
                self.state = new_state
            except TimeoutError:
                if self._result_capture_attempts > 9:
                    self.state = states.FAILURE
                else:
                    self._result_capture_attempts += 1
                self.save()

        if self.state != current_state:
            self.save()

    class Meta:
        verbose_name = 'Celery Task'
        verbose_name_plural = 'Celery Tasks'
        db_table = 'django_spire_celery_task'
        ordering = ('-started_datetime',)
