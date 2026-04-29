from abc import ABC

from celery.execute import send_task
from django.apps import apps
from django.db.models import Model

from django_spire.celery.models import CeleryTask


class BaseCeleryTaskManager(ABC):
    task_name: str
    app_name: str

    @property
    def reference_key(self) -> str:
        return CeleryTask.generate_reference_key(
            app_name=self.app_name,
            reference_name=self.reference_name,
            model_object=self.model_object,
        )

    @property
    def reference_name(self) -> str:
        return self.__class__.__name__.lower()

    def __init_subclass__(cls, **kwargs) -> None:
        required_class_attributes = ('celery_task_name', 'app_name', 'reference_name')

        for attribute_name in required_class_attributes:
            if not isinstance(getattr(cls, attribute_name), str):
                message = f'{cls.__name__}.{attribute_name} must be set and type string'
                raise TypeError(message)

    def __init__(self, model_object: Model | None = None) -> None:
        if not apps.is_installed(self.app_name):
            message = f'Celery task app_name "{self.app_name}" is invalid or not installed'
            raise ValueError(message)

        self.model_object = model_object

    def send_task(self, *args, **kwargs) -> None:
        async_result = send_task(name=self.task_name, args=args, kwargs=kwargs)

        CeleryTask.register(
            async_result=async_result,
            app_name=self.app_name,
            reference_name=self.__class__.__name__.lower(),
            model_object=self.model_object,
        )
