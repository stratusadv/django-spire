from __future__ import annotations

from functools import partial
from inspect import signature
from typing import Callable, TypeVar

from django_spire.core.injection.injector import BaseInjector


TDependency = TypeVar('TDependency')


class DependencyInjector(BaseInjector[Callable]):
    def __init__(
            self,
            target_dependency_type: type,
            dependency_factory: Callable[[], TDependency],
            injector_target: Callable = None,
            *args,
            **kwargs
    ):
        super().__init__(injector_target=injector_target, *args, **kwargs)


        if not callable(dependency_factory):
            raise TypeError(
                f'Invalid dependency_factory {dependency_factory} -'
                f' must be a callable.'
            )

        dependency_test = dependency_factory()

        if not isinstance(dependency_test, target_dependency_type):
            raise TypeError(
                f'Invalid dependency_factory {dependency_factory} -'
                f' must return an instance of {target_dependency_type}.'
            )

        self._dependency_factory = dependency_factory
        self._target_dependency_type = target_dependency_type

    def _find_callable_args_matching_dependency_type(
            self,
            target_callable: Callable,
    ) -> list[str]:
        callable_signature = signature(target_callable)

        arg_matches = [
            arg_name
            for arg_name, arg_type in callable_signature.parameters.items()
            if arg_type.annotation == self._target_dependency_type
        ]

        return arg_matches

    def _inject(
            self,
            injector_target: Callable,
            *args,
            **kwargs
    ) -> Callable:
        if not callable(injector_target):
            raise TypeError(
                f'Invalid target_callable {injector_target} - must be a callable'
            )

        callable_args_matching_dependency_type = self._find_callable_args_matching_dependency_type(
            injector_target
        )

        if len(callable_args_matching_dependency_type) == 0:
            return injector_target

        if not len(callable_args_matching_dependency_type) == 1:
            raise TypeError(
                f'Invalid target_callable {injector_target} - '
                f'must have exactly one parameter of type {self._target_dependency_type}.'
            )

        original_dependency_arg_name = callable_args_matching_dependency_type.pop()

        return partial(injector_target, **{original_dependency_arg_name: self._dependency_factory()})