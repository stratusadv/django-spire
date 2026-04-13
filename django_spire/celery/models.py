import hashlib
from datetime import timedelta

from celery import states
from celery.result import AsyncResult
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.timezone import now

from django_spire.celery.querysets import CeleryTaskQuerySet
from django_spire.conf import settings


class CeleryTask(models.Model):
    task_id = models.UUIDField(editable=False)
    reference_key = models.CharField(max_length=128)

    app_name = models.CharField(max_length=128)
    reference_name = models.CharField(max_length=128)

    state = models.CharField(max_length=16, choices=((state, state) for state in states.ALL_STATES), default=states.PENDING)
    started_datetime = models.DateTimeField(default=now)
    completed_datetime = models.DateTimeField(null=True, blank=True)
    estimated_completion_datetime = models.DateTimeField(default=now)

    objects = CeleryTaskQuerySet.as_manager()

    def __str__(self) -> str:
        return f'{self.app_name} > {self.reference_key}'

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
    def reference_name_display(self) -> str:
        return self.reference_name.replace('_', ' ').title()

    @property
    def estimated_completion_percentage(self) -> float:
        percentage = (self.estimated_time_seconds - self.estimated_time_remaining_seconds) / self.estimated_time_seconds

        if percentage > 1.0:
            percentage = 1.0

        if percentage < 0.0:
            percentage = 0.0

        return percentage

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

    @staticmethod
    def generate_reference_key(
            app_name: str,
            reference_name: str,
            model_object: models.Model | None = None,
    ) -> str:
        hashable_string = app_name

        hashable_string += reference_name.lower()

        if model_object:
            hashable_string += f'.{model_object.__class__.__name__}.{model_object.pk}'

        hashable_string += settings.SECRET_KEY

        return hashlib.md5(hashable_string.encode()).hexdigest()

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
            app_name: str,
            reference_name: str,
            model_object: models.Model | None = None,
            estimated_completion_seconds: int | None = None,
    ) -> None:
        cls.validate_register_arguments(
            app_name=app_name,
            reference_name=reference_name,
        )

        reference_key = cls.generate_reference_key(
            app_name=app_name,
            model_object=model_object,
            reference_name=reference_name,
        )

        cls.objects.create(
            app_name=app_name,
            reference_key=reference_key[:128],
            reference_name=reference_name[:128],
            task_id=async_result.id,
            estimated_completion_datetime=now() + timedelta(
                seconds=estimated_completion_seconds + 3) if estimated_completion_seconds else None,
        )

    @staticmethod
    def validate_register_arguments(
            app_name: str,
            reference_name: str,
    ):
        if not apps.is_installed(app_name):
            message = f'Celery task app_name "{app_name}" is invalid or not installed'
            raise ImproperlyConfigured(message)

        if any(char in reference_name for char in ' -'):
            message = f'Celery task reference_name "{reference_name}" has an invalid format, use "something_like_this" with only characters and underscores'
            raise ValueError(message)

    def update_from_async_result(self) -> None:
        new_state = self.async_result.state

        if self.state != states.SUCCESS and new_state == states.SUCCESS:
            self.completed_datetime = now()

        self.state = new_state

    def update_from_async_result_and_save(self) -> None:
        current_state = self.state

        self.update_from_async_result()

        if self.state != current_state:
            self.save()

    class Meta:
        ordering = ('-started_datetime',)
