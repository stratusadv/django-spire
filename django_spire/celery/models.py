import hashlib
import uuid

from celery.result import AsyncResult
from django.db import models
from django.utils.timezone import now

from django_spire.conf import settings


class CeleryTask(models.Model):
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    object_hash = models.CharField(max_length=128)
    reference_name = models.CharField(max_length=128)
    task_id = models.UUIDField(editable=False)

    class StatusChoices(models.TextChoices):
        PENDING = ('PENDING', 'Pending')
        SUCCESS = ('SUCCESS', 'Success')
        FAILURE = ('FAILURE', 'Failure')

    status = models.CharField(max_length=10, choices=StatusChoices, default=StatusChoices.PENDING)
    started_datetime = models.DateTimeField(default=now)
    finished_datetime = models.DateTimeField(null=True, blank=True)
    estimated_completion_datetime = models.DateTimeField(null=True, blank=True)

    @classmethod
    def register(
            cls,
            async_result: AsyncResult,
            app_label: str,
            reference_name: str,
            model_object: models.Model | None = None,
    ) -> None:
        object_hash = cls.generate_hash(
            app_label=app_label,
            model_object=model_object,
            reference_name=reference_name,
        )

        cls.objects.create(
            object_hash=object_hash[:128],
            reference_name=reference_name[:128],
            task_id=async_result.id,
        )

    @staticmethod
    def generate_hash(
            app_label: str,
            reference_name: str,
            model_object: models.Model | None = None,
    ) -> str:
        hashable_string = f'{app_label}.{reference_name}'

        if model_object:
            hashable_string += f'.{model_object.__class__.__name__}.{model_object.pk}'

        hashable_string += settings.SECRET_KEY

        return hashlib.md5(hashable_string.encode()).hexdigest()

    def update_status_from_result(self) -> None:
        result = AsyncResult(str(self.task_id))
        self.status = result.status

    class Meta:
        ordering = ('-started_datetime',)