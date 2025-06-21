from __future__ import annotations

import inspect
import sys
import typing
from abc import ABC
from typing import Any, ForwardRef, get_type_hints

from django_spire.contrib.service.exceptions import ServiceException


"""
Forward ref happens when we use if TYPE_CHECKING.
The string gets resolved in the future to an actual type.
"""


class BaseService(ABC):
    def __init_subclass__(cls) -> None:  # noqa: D401 imperative mood
        super().__init_subclass__()
        # Need to set class up to skip Future Refs
        cls._is_type_forward_ref = False

        # Descriptor workaround – unchanged
        def __get__(self, instance, owner):
            if instance is None:
                target: BaseService | Any = owner()
            else:
                target = instance

            if issubclass(target.__class__, BaseService):
                self._validate_target_or_error(target)
                return cls(getattr(target, self._obj_name))
            return cls(target)

        setattr(cls, "__get__", __get__)

        # Check if abstract
        if cls._is_abstract_class():
            return

        non_service = 0

        for ann in cls.__annotations__.values():
            if isinstance(ann, str):
                cls._is_type_forward_ref = True
                continue

            if not cls._is_service(ann):
                non_service += 1

        # Must have one non_service
        if not cls._is_type_forward_ref and non_service != 1:
            raise ServiceException(
                f"{cls.__name__} must have exactly one non‑BaseService annotated."
                f" Found {non_service}."
            )


    @classmethod
    def _is_service(cls, t: object) -> bool:
        return isinstance(t, type) and issubclass(t, BaseService)

    @classmethod
    def _is_abstract_class(cls):
        return ABC in cls.__bases__ or inspect.isabstract(cls.__class__)

    def __init__(self, obj: Any | None = None):
        self._obj_name: str = ""
        # Forward Ref is the type passed when we use __future__
        self._obj_type: type | ForwardRef | str

        if self._is_abstract_class():
            return


        if not self.is_future_ref and self._obj_is_valid:
            self._set_obj_from_annotations(obj)
        else:
            raise ServiceException(
                f"{self._obj_name} must be of same type {self.__class__.__name__}"
            )


        if getattr(self.__class__, "_is_type_forward_ref", False) and self._obj_is_resolved:
            self.__class__._is_type_forward_ref = False
            annotations = self.__class__._resolved_annotations()
            non_service = [
                t for t in annotations.values() if not self.__class__._is_service(t)
            ]
            if len(non_service) != 1:
                raise ServiceException(
                    f"{self.__class__.__name__} must have exactly one non‑BaseService "
                    f"annotated attribute. Found {len(non_service)}."
                )

    @property
    def obj(self) -> Any | None:  # May be None until late‑binding resolves
        return getattr(self, self._obj_name)

    @property
    def _obj_is_resolved(self) -> bool:
        return not self.__class__('_is_forward_ref') and isinstance(self._obj_type, type)

    @property
    def _obj_is_valid(self) -> bool:
        return self._obj_is_resolved and isinstance(self.obj, self._obj_type)

    @property
    def is_future_ref(self) ->bool:
        return getattr(self.__class__, "_is_type_forward_ref", False)

    def _set_obj_from_annotations(self, obj: Any | None = None) -> None:
        # If the object is None I want to initalize the type.

        annotations = self.__class__._resolved_annotations()

        for name, typ in annotations.items():
            if self.__class__._is_service(typ):
                continue
            self._obj_name = name
            self._obj_type = typ
            break
        else:
            raise ServiceException(
                f"{self.__class__.__name__} must declare exactly one annotated "
                f"attribute that is *not* a BaseService subclass."
            )

        # If we have a concrete class and caller didn't supply an object → autocreate
        if self._obj_is_resolved:
            if obj is None:
                setattr(self, self._obj_name, self._obj_type())
            else:
                setattr(self, self._obj_name, obj)
        else:
            # Still unresolved forward ref → just store what we have (or None)
            setattr(self, self._obj_name, obj)
            # Ensure late validation once the ref is resolved
            self.__class__._is_type_forward_ref = True

    def _validate_target_or_error(self, target: "BaseService" | Any) -> None:
        if target._obj_name != self._obj_name:
            raise ServiceException(
                f"{target.__class__.__name__} is required to have the same obj name "
                f"as {self.__class__.__name__}. \"{target._obj_name}\" is not "
                f"\"{self._obj_name}\"."
            )
        if self._obj_is_resolved and target._obj_is_resolved and target._obj_type != self._obj_type:
            raise ServiceException(
                f"{target.__class__.__name__} must use the same obj type as "
                f"{self.__class__.__name__}. {target._obj_type} is not {self._obj_type}."
            )
