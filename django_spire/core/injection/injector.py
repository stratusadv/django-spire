from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

TInjectorTarget = TypeVar('TInjectorTarget')


class BaseInjector(Generic[TInjectorTarget], ABC):
    @property
    def target(self) -> TInjectorTarget:
        return self._injector_target

    @classmethod
    def validate_target_type(cls, target: TInjectorTarget = None):
        if target is None:
            return

        if cls.__orig_bases__[0] == type(target):
            raise TypeError(f'Invalid injector_target {target} '
                            f'- must be not callable.')

    def __init__(
            self,
            injector_target: TInjectorTarget = None,
            *args,
            **kwargs
    ):
        self.validate_target_type(injector_target)
        self._injector_target: TInjectorTarget = injector_target

    def __call__(self, *args, **kwargs) -> TInjectorTarget:
        return self.inject(*args, **kwargs)

    @abstractmethod
    def _inject(self, injector_target: TInjectorTarget, *args, **kwargs) -> TInjectorTarget:
        raise NotImplementedError

    def inject(
            self,
            injector_target: TInjectorTarget = None,
            *args,
            **kwargs
    ) -> TInjectorTarget:
        if injector_target is None and self._injector_target is None:
            raise ValueError(
                f'Can\'t inject - no injector_target passed to {self.__class__.__name__}.'
                f'Either pass injector_target to {self.__class__.__name__} or'
                f'pass injector_target to {self.__class__.__name__}.inject'
            )

        if injector_target is None:
            injector_target = self._injector_target

        self.validate_target_type(injector_target)

        return self._inject(injector_target, *args, **kwargs)