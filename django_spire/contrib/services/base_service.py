from __future__ import annotations

from abc import abstractmethod
from typing import Type

from django.db.models import Model

from django_spire.contrib.services.default_service import DefaultService


class BaseService:

    @abstractmethod
    def __init__(self, *arg):
        raise NotImplementedError('You must pass the model class or model instance to the service constructor.')

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
