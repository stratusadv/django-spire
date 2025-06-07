from __future__ import annotations

from abc import ABC
from typing import Any

from django_spire.contrib.service.exceptions import ServiceException


class BaseService(ABC):
    def __init__(self, obj = None):
        print('__init__ triggered')
        print(self.__class__.__name__)

        for obj_name, obj_type in self.__class__.__annotations__.items():
            if not issubclass(obj_type, BaseService):
                self._obj_name = obj_name
                self._obj_type = obj_type

        if obj is not None:
            setattr(self, self._obj_name, obj)
        else:
            setattr(self, self._obj_name, self._obj_type())

        if not self._obj_is_valid:
            raise ServiceException('service validation failed')

    def __init_subclass__(cls):
        super().__init_subclass__()

        non_base_service_objects_count = 0
        for obj_name, obj_type in cls.__annotations__.items():
            if not issubclass(obj_type, BaseService):
                non_base_service_objects_count += 1

        if non_base_service_objects_count > 1:
            raise ValueError('only one non base service annotation allowed on a service')

        def __get__(self, instance, owner):
            if instance is None:
                target = owner()
            else:
                target = instance

            print('__get__ triggered')
            print(cls.__name__)
            print(f'{target=}')

            if issubclass(target.__class__, BaseService):
                return cls(
                    getattr(target, self._obj_name)
                )

            return cls(target)

        setattr(cls, '__get__', __get__)

    @property
    def obj(self) -> Any:
        return getattr(self, self._obj_name)

    @property
    def _obj_is_valid(self) -> bool:
        return isinstance(self.obj, self._obj_type)


