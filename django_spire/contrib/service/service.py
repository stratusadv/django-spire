from __future__ import annotations

"""BaseService – fourth‑iteration (handles *unresolved* forward refs during instantiation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This revision fixes the last crash you saw:
``TypeError: 'ForwardRef' object is not callable``
which happened when a concrete service was instantiated **before** its domain
model class existed.  We now:

* Detect when the selected ``_obj_type`` is still a ``str``/``ForwardRef``.
* Defer object creation *and* validation in that case, populating the attribute
  with ``None`` (or the caller‑supplied object).
* Perform the missing validation and default‑construction later, the first time
  the service is accessed *after* all models are loaded.
"""

import inspect
import sys
import typing
from abc import ABC
from typing import Any, ForwardRef, get_type_hints

from django_spire.contrib.service.exceptions import ServiceException


class BaseService(ABC):
    """Smart façade that injects a domain object into a *service* instance."""

    # ---------------------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------------------
    @classmethod
    def _is_service(cls, t: object) -> bool:
        return isinstance(t, type) and issubclass(t, BaseService)

    @classmethod
    def _resolved_annotations(cls) -> dict[str, type | ForwardRef | str]:
        try:
            return get_type_hints(
                cls,
                globalns=sys.modules[cls.__module__].__dict__,
                localns=cls.__dict__,
                include_extras=True,
            )
        except (NameError, AttributeError):
            out: dict[str, type | ForwardRef | str] = {}
            for name, ann in cls.__annotations__.items():
                if isinstance(ann, str):
                    ann = ForwardRef(ann)
                try:
                    out[name] = typing.evaluate_forward_ref(
                        ann, sys.modules[cls.__module__].__dict__, cls.__dict__
                    )
                except (NameError, AttributeError):
                    out[name] = ann
            return out

    # ------------------------------------------------------------------
    # Metaclass – phase 1 validation
    # ------------------------------------------------------------------
    def __init_subclass__(cls) -> None:  # noqa: D401 imperative mood
        super().__init_subclass__()

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

        if ABC in cls.__bases__ or inspect.isabstract(cls):
            cls._needs_late_validation = False
            return

        cls._needs_late_validation = False
        non_service = 0
        for ann in cls.__annotations__.values():
            if isinstance(ann, str):
                cls._needs_late_validation = True
                continue
            if not cls._is_service(ann):
                non_service += 1
        if not cls._needs_late_validation and non_service != 1:
            raise ServiceException(
                f"{cls.__name__} must have exactly one non‑BaseService annotated "
                f"attribute. Found {non_service}."
            )

    # ------------------------------------------------------------------
    # Instance construction – phase 2 validation
    # ------------------------------------------------------------------
    def __init__(self, obj: Any | None = None):
        self._obj_name: str = ""
        self._obj_type: type | ForwardRef | str

        if ABC in self.__class__.__bases__ or inspect.isabstract(self.__class__):
            return

        self._set_obj_from_annotations(obj)

        if self._obj_is_resolved and not self._obj_is_valid:
            raise ServiceException(
                f"{self._obj_name} failed to validate on {self.__class__.__name__}"
            )

        if getattr(self.__class__, "_needs_late_validation", False) and self._obj_is_resolved:
            self.__class__._needs_late_validation = False
            annotations = self.__class__._resolved_annotations()
            non_service = [
                t for t in annotations.values() if not self.__class__._is_service(t)
            ]
            if len(non_service) != 1:
                raise ServiceException(
                    f"{self.__class__.__name__} must have exactly one non‑BaseService "
                    f"annotated attribute. Found {len(non_service)}."
                )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def obj(self) -> Any | None:  # May be None until late‑binding resolves
        return getattr(self, self._obj_name)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    @property
    def _obj_is_resolved(self) -> bool:
        return isinstance(self._obj_type, type)

    @property
    def _obj_is_valid(self) -> bool:
        return not self._obj_is_resolved or isinstance(self.obj, self._obj_type)

    def _set_obj_from_annotations(self, obj: Any | None = None) -> None:
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
            self.__class__._needs_late_validation = True

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
