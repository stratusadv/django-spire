import hashlib
from abc import ABC

from celery.execute import send_task
from celery.result import AsyncResult
from django.conf import settings
from django.db import models
from django.db.models import Model

from django_spire.celery.models import CeleryTask


class BaseCeleryTaskManager(ABC):
    task_name: str
    display_name: str
    estimated_completion_seconds: int | None = None

    @property
    def reference_key(
            self,
    ) -> str:
        hashable_string = self.task_name

        hashable_string += self.__class__.__name__

        if self.model_object:
            hashable_string += f'.{self.model_object.__class__.__name__}.{self.model_object.pk}'

        hashable_string += settings.SECRET_KEY

        return hashlib.md5(hashable_string.encode()).hexdigest()

    def __init_subclass__(cls, **kwargs) -> None:
        required_class_attributes = ('task_name', 'display_name')

        for attribute_name in required_class_attributes:
            if not isinstance(getattr(cls, attribute_name), str):
                message = f'{cls.__name__}.{attribute_name} must be set and type string'
                raise TypeError(message)

    def __init__(self, model_object: Model | None = None) -> None:
        self.model_object = model_object

    def send_task(self, *args, **kwargs) -> AsyncResult:
        async_result = send_task(name=self.task_name, args=args, kwargs=kwargs)

        CeleryTask.register(
            async_result=async_result,
            task_name=self.task_name,
            display_name=self.display_name,
            reference_key=self.reference_key,
            estimated_completion_seconds=self.estimated_completion_seconds,
        )

        return async_result
