from __future__ import annotations

from abc import ABC
from typing import Any, cast


class BaseService(ABC):
    class_setup: bool = False

    def __init__(self, obj: Any = None):
        """
            Rules
            - First annotated class attribute must be the target object
            - Must have the same target object name as the class name?
            - Target type must be the same type as the object?
        """

        # Object will be initialized on the __get__ call
        if obj is None:
            return

        self._obj_name: str = list(self.__class__.__annotations__.keys())[0]
        self._obj_type: type = obj.__class__

        setattr(self, self._obj_name, obj)

        target_class = obj.__class__
        setattr(self, target_class.__name__, target_class)

        # Cascade initializing services
        self._init_sub_services()

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

                # Caches the service and sub services onto the target object.
                if hasattr(target, cls._cache_key()):
                    return getattr(target, cls._cache_key())
                else:
                    instance = cls(target)
                    setattr(target, cls._cache_key(), instance)
                    return instance

            setattr(cls, '__get__', __get__)

    def _init_sub_services(self):
        for key, value in self.__class__.__annotations__.items():
            if isinstance(getattr(self, key), type) and issubclass(getattr(self, key), BaseService):
                setattr(self, key, getattr(self, key)(self.obj))

    @classmethod
    def _cache_key(cls):
        return f'{cls.__name__}_cache_key'

    @property
    def obj(self) -> Any:
        return getattr(self, self._obj_name)

    @property
    def obj_class(self) -> type:
        return self._obj_type

    @property
    def _obj_is_valid(self) -> bool:
        return isinstance(self.obj, self._obj_type)
