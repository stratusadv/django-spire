from __future__ import annotations

from abc import ABC
from typing import Any

from django_spire.contrib.service.exceptions import ServiceException


class BaseService(ABC):
    def __init__(self, obj: Any = None):
        self._obj_name: str = list(self.__class__.__annotations__.keys())[0]

        self._obj_type_str: str = str(
            list(self.__class__.__annotations__.values())[0]
        ).split('.')[-1]

        self._obj_type: type = ...

        if obj is None:
            return

        if obj.__class__.__name__ != self._obj_type_str:
            raise ServiceException(
                f'{self.__class__.__name__} was instantiated with obj type "{obj.__class__.__name__}" and failed as it was expecting "{self._obj_type_str}".'
            )

        self._obj_type: type = obj.__class__

        if self._obj_type is None or self._obj_type is ...:
            raise ServiceException(
                f'{self.__class__.__name__} top class attribute must have an annotated type.')

        # This will set a class attribute to match the annotation type
        # Example: "car: Car" will allow you to access "self.car" for the instance and "self.Car" for the class access.
        setattr(self, self._obj_type_str, self._obj_type)

        setattr(self, self._obj_name, obj)

        if ABC not in self.__class__.__bases__:
            if not self._obj_is_valid:
                raise ServiceException(f'{self._obj_name} failed to validate on {self.__class__.__name__}')

    def __init_subclass__(cls):
        super().__init_subclass__()

        if ABC not in cls.__bases__:
            # Typing Does not work properly for services if you override __get__ in the BaseService class.
            # This is a workaround and should be fixed in future versions of the python lsp.
            def __get__(self, instance, owner):

                if instance is None:
                    target: BaseService | Any = owner()
                else:
                    target: BaseService | Any = instance

                print(f'{target=}')

                if issubclass(target.__class__, BaseService):

                    self._validate_base_service_target_or_error(target)

                    return cls(getattr(target, self._obj_name))

                return cls(target)

            setattr(cls, '__get__', __get__)

    @property
    def obj(self) -> Any:
        return getattr(self, self._obj_name)

    @property
    def obj_class(self) -> Any:
        return getattr(self, self.obj.__class__.__name__)

    @property
    def _obj_is_valid(self) -> bool:
        return isinstance(self.obj, self._obj_type)

    def _validate_base_service_target_or_error(self, target: BaseService):
        if target._obj_name != self._obj_name:
            raise ServiceException(
                f'{target.__class__.__name__} is required to have the same obj name as {self.__class__.__name__}. "{target._obj_name}" is not "{self._obj_name}".')

        if target._obj_type_str != self._obj_type_str:
            raise ServiceException(
                f'{target.__class__.__name__} must use the same obj type as {self.__class__.__name__}. {target._obj_type} is not {self._obj_type}.')


