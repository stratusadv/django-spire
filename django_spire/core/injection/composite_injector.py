from abc import ABC
from typing import TypeVar, Any

from django_spire.core.injection.injector import BaseInjector

TInjectorTarget = TypeVar('TInjectorTarget')


class BaseCompositeInjector(BaseInjector[TInjectorTarget], ABC):
    allowed_child_injector_types = (BaseInjector,)

    def __init__(
            self,
            child_injectors: tuple[BaseInjector, ...] = (),
            injector_target: TInjectorTarget = None,
            *args,
            **kwargs
    ):
        super().__init__(injector_target, *args, **kwargs)

        if getattr(
            self.__class__, 'allowed_child_injector_types', None
        ) is not None:
            for child_injector_type in self.allowed_child_injector_types:
                if not issubclass(child_injector_type, BaseInjector):
                    raise TypeError(
                        f'Invalid child injector type assigned '
                        f'to {self.__class__}.allowed_child_injector_types.'
                        f'allowed_child_injector_types: {child_injector_type}. '
                        f'Child injectors for {self.__class__} must be of'
                        f'type {BaseInjector}.'
                    )
        else:
            setattr(
                self.__class__,
                'allowed_child_injector_types',
                (BaseInjector,)
            )

        self._child_injectors: dict[Any, list[BaseInjector]] = {}
        for injector in child_injectors:
            self.add_injector(injector)

    def __add__(self, other):
        if not isinstance(other, BaseCompositeInjector):
            self.add_injector(other)
        elif isinstance(other, BaseCompositeInjector):
            for injector_target, injector_list in other._child_injectors.items():
                for injector in injector_list:
                    self.add_injector(injector)
        else:
            raise TypeError(
                f'Can\'t add {other.__class__.__name__} to {self.__class__.__name__}'
            )

        return self

    def __getitem__(self, item: TInjectorTarget = None) -> list[BaseInjector]:
        if item is not None:
            injector_target_type = self.__class__.__orig_bases__[0]
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