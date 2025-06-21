from __future__ import annotations

from abc import ABC
from typing import Any


class BaseService(ABC):
    class_setup: bool = False

    def __init__(self, obj: Any = None):
        # Todo: Add check to see if it should be initialized.
        # Todo: Can I improve the performance on this?
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

        # Cascade initializing services
        self._init_sub_services()

    def __init_subclass__(cls):
        super().__init_subclass__()

        if ABC not in cls.__bases__:

            def __get__(self, instance, owner):
                if instance is None:
                    target: BaseService | Any = owner()
                else:
                    target: BaseService | Any = instance

                return cls(target)


            setattr(cls, '__get__', __get__)

    def _init_sub_services(self):
        for key, value in self.__class__.__annotations__.items():
            if isinstance(getattr(self, key), type) and issubclass(getattr(self, key), BaseService):
                setattr(self, key, getattr(self, key)(self.obj))

    @property
    def obj(self) -> Any:
        return getattr(self, self._obj_name)

    @property
    def _obj_is_valid(self) -> bool:
        return isinstance(self.obj, self._obj_type)
