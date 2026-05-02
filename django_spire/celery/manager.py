from typing import Any
import hashlib
from abc import ABC
from datetime import timedelta
from math import ceil

from celery.execute import send_task
from django.conf import settings
from django.db.models import Model, QuerySet
from django.utils.timezone import now

from django_spire.celery.models import CeleryTask

_CELERY_ESTIMATED_TIME_MULTIPLIER = 1.15


class BaseCeleryTaskManager(ABC):
    task_name: str
    display_name: str
    estimated_completion_seconds: int | None = None
    required_args_types: list[type] | None = None
    required_kwargs_keys_types: dict[str, type] | None = None

    def __init_subclass__(cls, **kwargs) -> None:
        required_class_attributes = ('task_name', 'display_name')

        for attribute_name in required_class_attributes:
            attr_value = getattr(cls, attribute_name, None)
            if not isinstance(attr_value, str):
                message = f'{cls.__name__}.{attribute_name} must be set and type string'
                raise TypeError(message)

    def __init__(self, model_object: Model | None = None) -> None:
        self.model_object = model_object

    @property
    def reference_key(self) -> str:
        hashable_string = self.task_name
        hashable_string += self.__class__.__name__
        hashable_string += settings.SECRET_KEY

        return hashlib.md5(hashable_string.encode()).hexdigest()[:128]

    @property
    def model_key(self) -> str | None:
        if self.model_object is not None:
            hashable_string = self.model_object.__class__.__name__
            hashable_string += str(self.model_object.pk)
            hashable_string += settings.SECRET_KEY

            return hashlib.md5(hashable_string.encode()).hexdigest()[:128]

        return None

    @property
    def reference_and_model_key(self) -> str:
        model_key = self.model_key

        if isinstance(model_key, str):
            return self.reference_key + '|' + model_key

        return self.reference_key

    @property
    def class_and_send_task_method(self) -> str:
        return f'{self.__class__.__name__}.send_task(*args, )'

    def filter_celery_tasks(self) -> QuerySet[CeleryTask]:
        return CeleryTask.objects.by_reference_keys_model_keys({self.reference_key: self.model_key})

    def send_task(self, *args, **kwargs) -> CeleryTask:
        self._validate_args_and_kwargs(*args, **kwargs)

        async_result = send_task(name=self.task_name, args=args, kwargs=kwargs)

        return CeleryTask.objects.create(
            task_id=async_result.id,
            task_name=self.task_name[:255],
            display_name=self.display_name[:255],
            reference_key=self.reference_key,
            model_key=self.model_key,
            estimated_completion_datetime=now()
            + timedelta(
                seconds=ceil(self.estimated_completion_seconds * _CELERY_ESTIMATED_TIME_MULTIPLIER)
            )
            if self.estimated_completion_seconds is not None
            else now(),
        )

    def _validate_args_and_kwargs(self, *args, **kwargs) -> None:
        if self.required_args_types and args:
            if len(args) != len(self.required_args_types):
                message = f'{self.class_and_send_task_method} only got {len(args)} arguments, expected {len(self.required_args_types)}'
                raise ValueError(message)

            for i, arg in enumerate(args):
                if not isinstance(arg, self.required_args_types[i]):
                    message = f'{self.class_and_send_task_method} method got invalid type from arg at position {i} must be type {self.required_args_types[i]}'
                    raise TypeError(message)

        if self.required_kwargs_keys_types and kwargs:
            for key, type_ in self.required_kwargs_keys_types.items():
                if key not in kwargs:
                    message = f'{self.class_and_send_task_method} method is missing kwarg "{key}"'
                    raise ValueError(message)

                if not isinstance(kwargs[key], type_):
                    message = f'{self.class_and_send_task_method} method got invalid type from kwarg "{key}" must be type {type_}'
                    raise TypeError(message)
