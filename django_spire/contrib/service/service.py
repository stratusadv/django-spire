from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Type

from django.db.models import Model

from django_spire.ai.chat.models import Chat
from django_spire.contrib.service.default_service import DefaultService
from django_spire.contrib.service.exceptions import ServiceException


class BaseService(ABC):
    obj_class: Type
    obj_name: str

    def __init__(self, *arg):
        self.__dict__.update({
            self.obj_name: self.obj_class
        })
        setattr(self, self.obj_name, self.obj_class())

    def __init_subclass__(cls):
        super().__init_subclass__()
        for attr in ['obj_class', 'obj_name']:
            if getattr(cls, attr) is None:
                raise ServiceException(f'{cls.__name__}.{attr} is required and is not set properly.')


    @staticmethod
    def is_ready_instance(obj: Model | Type[Model]):
        from django.db.models import Model
        return isinstance(obj, Model) and obj.id is not None

    @staticmethod
    def is_new_instance(obj : Model | Type[Model]):
        return obj.id is None

    @staticmethod
    def is_class_instance(obj: Model | Type[Model]):
        return isinstance(obj, type) and issubclass(obj, Model)

    @property
    def default(self):
        return DefaultService()