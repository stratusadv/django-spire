from __future__ import annotations

from abc import ABC
from typing import Any

from django_spire.contrib.service.exceptions import ServiceException


class BaseService(ABC):
    def __init__(self, obj: Any = None):
        self._obj_name: str = ...
        self._obj_type: type = ...

        if ABC not in self.__class__.__bases__:
            self._set_obj_from_annotations(obj)

            if not self._obj_is_valid:
                raise ServiceException(f'{self._obj_name} failed to validate on {self.__class__.__name__}')

    def __init_subclass__(cls):
        super().__init_subclass__()

        if ABC not in cls.__bases__:
            cls._validate_annotations_or_error()

            # Typing Does not work properly for services if you override __get__ in the BaseService class.
            # This is a workaround and should be fixed in future versions of the python lsp.
            def __get__(self, instance, owner):
                if instance is None:
                    target: BaseService | Any = owner()
                else:
                    target: BaseService | Any = instance

                if issubclass(target.__class__, BaseService):

                    self._validate_target_or_error(target)

                    return cls(getattr(target, self._obj_name))

                return cls(target)

            setattr(cls, '__get__', __get__)

    @property
    def obj(self) -> Any:
        return getattr(self, self._obj_name)

    @property
    def _obj_is_valid(self) -> bool:
        return isinstance(self.obj, self._obj_type)

    def _set_obj_from_annotations(self, obj: Any = None):
        for obj_name, obj_type in self.__class__.__annotations__.items():
            if not issubclass(obj_type, BaseService):
                self._obj_name = obj_name
                self._obj_type = obj_type
                break

        if self._obj_type is None:
            raise ServiceException(
                f'{self.__class__.__name__} annotated class attribute cannot be type None.')

        if obj is None:
            setattr(self, self._obj_name, self._obj_type())
        else:
            setattr(self, self._obj_name, obj)

    @classmethod
    def _validate_annotations_or_error(cls):
        non_base_service_objects_count = 0

        for obj_name, obj_type in cls.__annotations__.items():
            if not issubclass(obj_type, BaseService):
                non_base_service_objects_count += 1

        if non_base_service_objects_count != 1:
            raise ServiceException(
                f'{cls.__name__} must have exactly one non-BaseService annotated class attribute. Found {non_base_service_objects_count}'
            )

    def _validate_target_or_error(self, target: BaseService | Any):
        if target._obj_name != self._obj_name:
            raise ServiceException(
                f'{target.__class__.__name__} is required to have the same obj name as {self.__class__.__name__}. "{target._obj_name}" is not "{self._obj_name}".')

        if target._obj_type != self._obj_type:
            raise ServiceException(
                f'{target.__class__.__name__} must use the same obj type as {self.__class__.__name__}. {target._obj_type} is not {self._obj_type}.')
