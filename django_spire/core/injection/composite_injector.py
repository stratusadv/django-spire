from abc import ABC, abstractmethod
from typing import Tuple, TypeVar

from django.urls import URLResolver, URLPattern

from django_spire.core.injection.injector import BaseInjector
from django_spire.core.utils import get_generic_type_args

URLConf = Tuple[URLPattern | URLResolver, ...] | URLPattern | URLResolver

TInjectorTarget = TypeVar('TInjectorTarget')


class BaseCompositeInjector(BaseInjector[TInjectorTarget], ABC):
    allowed_child_injector_types = (BaseInjector,)

    def __init__(
            self,
            child_injectors: tuple[BaseInjector, ...] = (),
            injector_target: URLConf = None,
            *args,
            **kwargs
    ):
        super().__init__(injector_target, *args, **kwargs)

        if getattr(self.__class__, 'allowed_child_injector_types',
                   None) is not None:
            for child_injector_type in self.allowed_child_injector_types:
                if not issubclass(child_injector_type, BaseInjector):
                    raise TypeError(
                        f'Invalid child injector type passed to {self.__class__} '
                        f'allowed_child_injector_types: {child_injector_type}. '
                        f'Child injectors for {self.__class__.__name__} must be {BaseInjector}'
                    )

        self._child_injectors = {}
        for injector in child_injectors:
            self.add_injector(injector)

    def __add__(self, other: BaseInjector) -> BaseInjector:
        self.add_injector(other)
        return self

    def __getitem__(self, item: TInjectorTarget = None) -> list[BaseInjector]:
        if item is not None:
            injector_target_type = get_generic_type_args(self.__class__, 0)
            if not isinstance(item, injector_target_type):
                raise IndexError(
                    f'Invalid injector index passed to {self.__class__.__name__}: {item}. '
                    f'Indexes for {self.__class__.__name__} must be {injector_target_type}'
                )

        return self._child_injectors.get(item, [])

    def add_injector(
            self,
            injector: BaseInjector,
            *args,
            **kwargs
    ) -> None:
        if not hasattr(self.__class__, 'allowed_child_injector_types'):
            raise AttributeError(
                f'{self.__class__.__name__} does not support adding child injectors.'
            )

        if type(injector) not in self.__class__.allowed_child_injector_types:
            raise TypeError(
                f'Invalid injector passed to {self.__class__.__name__}: {injector}. '
                f'Injectors added to {self.__class__.__name__} must '
                f'one of {self.allowed_child_injector_types}'
            )

        if not hasattr(self, '_child_injectors'):
            setattr(self, '_child_injectors', {})

        if injector.target not in self._child_injectors:
            self._child_injectors[injector.target] = []

        self._child_injectors[injector.target].append(injector)