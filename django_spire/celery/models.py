import hashlib
import uuid

import celery
from django.db import models
from django.utils.timezone import now

from django_spire.conf import settings


class CeleryTask(models.Model):
    object_hash = models.TextField()
    task_name = models.TextField()
    task_id = models.UUIDField(editable=False)

    class StatusChoices(models.TextChoices):
        PENDING = ('PENDING', 'Pending')
        SUCCESS = ('SUCCESS', 'Success')
        FAILURE = ('FAILURE', 'Failure')

    status = models.CharField(max_length=10, choices=StatusChoices, default=StatusChoices.PENDING)
    started_datetime = models.DateTimeField(default=now)
    finished_datetime = models.DateTimeField(null=True, blank=True)
    estimated_completion_datetime = models.DateTimeField(null=True, blank=True)

    def register(
            self,
            celery_task: celery.Task,
            app_label: str,
            model_object: models.Model | None = None,
            task_name: str | None = None,
    ) -> None:
        if app_label is None and model_object is None and  task_name is None:
            raise ValueError('CeleryTask.register requires `app_label` and `model_object` or `task_name`')

    @staticmethod
    def _object_hash(
            django_model_object: models.Model | None = None,
            app_label: str | None = None,
            reference_name: str | None = None,
    ) -> str | None:
        hashable_string: str = ''

        if django_model_object:
            hashable_string = f'{django_model_object.__class__.__name__}.{django_model_object.pk}'

        elif app_label and reference_name:
            hashable_string = f'{app_label}.{reference_name}'

        if len(hashable_string) > 0:
            hashable_string += settings.SECRET_KEY
            return hashlib.md5(hashable_string.encode()).hexdigest()

        return None

