from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Type, TypedDict

from django.contrib.auth.models import User
from django.db.models import Model

from django_spire.ai.chat.models import Chat
from django_spire.contrib.service.default_service import DefaultService
from django_spire.contrib.service.descriptor import ServiceDescriptor
from django_spire.contrib.service.exceptions import ServiceException


class BaseService(ABC):
    obj_class: type
    obj_name: str

    @abstractmethod
    def __init__(self, *arg):
        raise NotImplementedError

    def __init_subclass__(cls):
        super().__init_subclass__()
        for attr in ['obj_class', 'obj_name']:
            if getattr(cls, attr) is None:
                raise ServiceException(f'{cls.__name__}.{attr} is required and is not set properly.')

    def __new__(cls, *args, **kwargs):
        return ServiceDescriptor(cls)

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
