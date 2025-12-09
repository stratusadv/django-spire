from __future__ import annotations

from abc import ABC
from typing import Any, Generic, TypeVar

from django_spire.contrib.constructor.exceptions import ConstructorError


TypeAny = TypeVar('TypeAny', bound=Any, covariant=True)


class BaseConstructor(
    ABC,
    Generic[TypeAny]
):
    def __init__(self, obj: Any = None):
        self._obj_type_name: str = str(
            next(iter(self.__class__.__annotations__.values()))
        ).split('.')[-1]

        if obj is None:
            return

        self._obj_mro_type_names = [cls.__name__ for cls in obj.__class__.__mro__]

        if self._obj_type_name not in self._obj_mro_type_names:
            message = f'{self.__class__.__name__} was instantiated with obj type "{obj.__class__.__name__}" and failed as it was expecting "{self._obj_type_name}".'
            raise ConstructorError(message)

        self._obj_type: type[TypeAny] = obj.__class__

        if self._obj_type is None or self._obj_type is ...:
            message = f'{self.__class__.__name__} top class attribute must have an annotated type.'
            raise ConstructorError(message)

        self.obj: TypeAny = obj

        if ABC not in self.__class__.__bases__:
            if not self._obj_is_valid:
                message = f'{self._obj_type_name} failed to validate on {self.__class__.__name__}'
                raise ConstructorError(message)

        self.__post_init__()

    def __init_subclass__(cls):
        super().__init_subclass__()

        if ABC not in cls.__bases__:
            if 'obj' not in cls.__annotations__:
                message = f'{cls.__name__} must have an "obj" attribute annotated with a type.'
                raise ConstructorError(message)

            # Typing Does not work properly for services if you override __get__ in the BaseService class.
            # This is a workaround and should be fixed in future versions of the python lsp.
            def __get__(self, instance, owner):

                if instance is None:
                    target: cls | Any = owner()
                else:
                    target: cls | Any = instance

                if issubclass(target.__class__, BaseConstructor):

                    self._validate_base_service_target_or_error(target)

                    return cls(target.obj)

                return cls(target)

            cls.__get__ = __get__

    def __post_init__(self):
        pass

    @property
    def obj_class(self) -> type[TypeAny]:
        return self._obj_type

    @property
    def _obj_is_valid(self) -> bool:
        return isinstance(self.obj, self._obj_type)

    def _validate_base_service_target_or_error(self, target: BaseConstructor):
        if self._obj_type_name not in target._obj_mro_type_names:
            message = f'{target.__class__.__name__} must use the same obj type as {self.__class__.__name__}. {self._obj_type_name} is not in {target._obj_mro_type_names}'
            raise ConstructorError(message)
