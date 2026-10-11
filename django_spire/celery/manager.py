from __future__ import annotations

import hashlib
import pickle
import time
import uuid
from abc import ABC
from typing import Any

from celery import states
from celery.exceptions import BackendError
from celery.exceptions import OperationalError as CeleryOperationalError
from celery.exceptions import TimeoutError as CeleryTimeoutError
from celery.execute import send_task
from django.conf import settings
from django.db.models import Model, QuerySet
from django.utils.timezone import now
from kombu.exceptions import ChannelError
from kombu.exceptions import ConnectionError as KombuConnectionError
from pydantic import create_model, BaseModel

from django_spire.celery.models import CeleryTask
from django_spire.celery.result import CeleryExceptionResult, SendFailedError

_MAX_SEND_TASK_RETRIES = 5

_SEND_RETRYABLE_EXCEPTIONS = (
    CeleryOperationalError,
    KombuConnectionError,
    ChannelError,
    CeleryTimeoutError,
    BackendError,
    ConnectionError,
    OSError,
)


class BaseCeleryTaskManager(ABC):
    """Used for creating a rigid structure in the client code for calling celery tasks on remote workers"""

    task_name: str
    display_name: str
    required_kwargs_keys_types: dict[str, type] | None = None
    send_task_retries: int = 2
    dedupe_unready: bool = False

    def __init_subclass__(cls, **kwargs) -> None:
        required_class_attributes = ('task_name', 'display_name')

        for attribute_name in required_class_attributes:
            attr_value = getattr(cls, attribute_name, None)
            if not isinstance(attr_value, str):
                message = f'{cls.__name__}.{attribute_name} must be set and type string'
                raise TypeError(message)

        if cls.send_task_retries > _MAX_SEND_TASK_RETRIES:
            message = f'{cls.__name__}.send_task_retries = {cls.send_task_retries} exceeded the maximum number {_MAX_SEND_TASK_RETRIES} of retries allowed'
            raise ValueError(message)

    def __init__(self, model_object: Model | None = None) -> None:
        self.model_object = model_object

    @property
    def reference_key(self) -> str:
        hashable_string = self.task_name
        hashable_string += self.__class__.__name__
        hashable_string += settings.SECRET_KEY

        return hashlib.md5(hashable_string.encode()).hexdigest()

    @property
    def model_key(self) -> str | None:
        if self.model_object is not None:
            hashable_string = self.model_object.__class__.__name__
            hashable_string += str(self.model_object.pk)
            hashable_string += settings.SECRET_KEY

            return hashlib.md5(hashable_string.encode()).hexdigest()

        return None

    @property
    def reference_and_model_key(self) -> str:
        model_key = self.model_key

        if isinstance(model_key, str):
            return self.reference_key + '|' + model_key

        return self.reference_key

    @property
    def class_and_send_task_method(self) -> str:
        return f'{self.__class__.__name__}.send_task(**kwargs)'

    @classmethod
    def create_pydantic_model_class(cls, model_name: str) -> type[BaseModel]:
        if cls.required_kwargs_keys_types is None:
            message = 'Cannot create pydantic model without required kwargs keys'
            raise ValueError(message)

        return create_model(
            model_name,
            **{key: (type_, ...) for key, type_ in cls.required_kwargs_keys_types.items()},
        )

    def filter_celery_tasks(self) -> QuerySet[CeleryTask]:
        return CeleryTask.objects.by_reference_keys_model_keys({self.reference_key: self.model_key})

    def _send_headers(self) -> dict[str, str]:
        headers = {
            'spire_reference_key': self.reference_key,
            'spire_display_name': self.display_name,
        }
        model_key = self.model_key
        if model_key is not None:
            headers['spire_model_key'] = model_key

        return headers

    def send_task(self, **kwargs) -> CeleryTask:
        self._validate_and_kwargs(**kwargs)

        if self.dedupe_unready:
            unready_task = self.filter_celery_tasks().by_unready().first()
            if unready_task is not None:
                return unready_task

        attempt = 0
        last_exception: Exception | None = None

        while attempt <= self.send_task_retries:
            try:
                async_result = send_task(
                    name=self.task_name, kwargs=kwargs, headers=self._send_headers()
                )
                return self._create_celery_task(async_result)
            except _SEND_RETRYABLE_EXCEPTIONS as e:
                attempt += 1
                last_exception = e

                if attempt > self.send_task_retries:
                    break

                time.sleep(1 * (2 ** (attempt - 1)))

        return self._create_failed_celery_task(
            error_message=str(last_exception) if last_exception else 'Unknown error'
        )

    def _create_celery_task(self, async_result: Any) -> CeleryTask:
        self._validate_model_object()

        return CeleryTask.objects.create(
            task_id=async_result.id,
            task_name=self.task_name[:255],
            display_name=self.display_name[:255],
            reference_key=self.reference_key,
            model_key=self.model_key,
        )

    def _create_failed_celery_task(self, error_message: str) -> CeleryTask:
        self._validate_model_object()

        failed_task_id = uuid.uuid4()
        exception = SendFailedError(error_message)
        exception_result = CeleryExceptionResult(
            exc=exception, einfo_pickle=None, traceback_text=None
        )

        return CeleryTask.objects.create(
            task_id=failed_task_id,
            task_name=self.task_name[:255],
            display_name=self.display_name[:255],
            reference_key=self.reference_key,
            model_key=self.model_key,
            state=states.FAILURE,
            started_datetime=now(),
            completed_datetime=now(),
            _result=pickle.dumps(exception_result),
        )

    def _validate_and_kwargs(self, **kwargs) -> None:
        if self.required_kwargs_keys_types and kwargs:
            for key, type_ in self.required_kwargs_keys_types.items():
                if key not in kwargs:
                    message = f'{self.class_and_send_task_method} method is missing kwarg "{key}"'
                    raise ValueError(message)

                if not isinstance(kwargs[key], type_):
                    message = f'{self.class_and_send_task_method} method got invalid type from kwarg "{key}" must be type {type_}'
                    raise TypeError(message)

    def _validate_model_object(self) -> None:
        if self.model_object is not None and self.model_object.pk is None:
            message = f'{self.__class__.__name__}.model_object "{self.model_object.__class__.__name__}" must have primary key'
            raise ValueError(message)
