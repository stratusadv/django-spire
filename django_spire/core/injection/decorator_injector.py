from typing import Callable, get_type_hints, Tuple, Iterable

from django_spire.core.injection.injector import BaseInjector

Decorator = Callable[
    [Callable],
    Callable
]


class DecoratorInjector(BaseInjector[Callable]):
    def __init__(
            self,
            decorators: Tuple[Decorator, ...] | Decorator,
            injector_target: Callable = None,
            *args,
            **kwargs
    ):
        super().__init__(injector_target=injector_target, *args, **kwargs)

        if not isinstance(decorators, tuple):
            decorators = (decorators,)

        for decorator in decorators:
            if not callable(decorator):
                raise TypeError(f'{decorator} is not callable.')

            decorator_annotations = get_type_hints(decorator)
            if 'return' not in decorator_annotations:
                raise TypeError(f'{decorator} must return a callable.')

            if not callable(decorator_annotations['return']):
                raise TypeError(f'{decorator_annotations["return"]} is not callable.')

        self._decorators = decorators

    def _inject(
            self,
            injector_target: Callable = None,
            *args,
            **kwargs
    ) -> Callable:
        for decorator in self._decorators:
            injector_target = decorator(injector_target)

        return injector_target
