from typing import Any, Generic, TypeVar

# class ServiceDescriptor:
#     def __init__(self, service_cls: type):
#         self._service_cls = service_cls
#
#     def __get__(self, instance, owner):
#         target = instance if instance is not None else owner
#
#         print('__get__ triggered')
#         print(self._service_cls(target))
#
#         return self._service_cls(target)
#
#
from abc import ABC, abstractmethod

T = TypeVar('T', bound='BaseService')

class BaseService(ABC):
    def __get__(self, instance, owner) -> T:
        print('__get__ triggered')
        target = instance if instance is not None else owner

        return self.__class__(target)

    def __init__(self, obj = None):
        print('__init__ triggered')
        print(self.__class__.__name__)
        print(self.__class__.__annotations__)

        for obj_name, obj_type in self.__class__.__annotations__.items():
            self.obj_name = obj_name
            self.obj_type = obj_type

        if obj is not None:
            setattr(self, self.obj_name, obj)

    def __init_subclass__(cls):
        super().__init_subclass__()

        if len(cls.__annotations__.items()) != 1:
            raise ValueError('only one annotation allowed on a service')

    def yehaw(self):
        print('yehaw triggered')

    # def __new__(cls, *args, **kwargs):
    #     print('__new__ triggered')
    #     instance = super().__new__(cls)
    #     return ServiceDescriptor(instance.__class__)


class JunkService(BaseService):
    junk: Any

    def crumbs(self) -> str:
        return self.junk.name


class Junk:
    services = JunkService()
    # services = ServiceDescriptor(JunkService)

    def __init__(self, name, parts):
        self.name=name
        self.parts=parts

new_junk = Junk('tacos', 10)

print(new_junk.services)
