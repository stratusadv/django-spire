from __future__ import annotations

from functools import partial
from typing import Callable, get_type_hints, Any, TypeVar, Generic, get_args

from django_spire.core.injection.injector import BaseInjector
from django_spire.core.utils import get_generic_type_args

TDependency = TypeVar('TDependency')

class DependencyInjector(BaseInjector, Generic[TDependency]):
    @staticmethod
    def callable_returns_type(
            target_callable: Callable,
            return_type: type
    ):
        callable_annotations = get_type_hints(target_callable)

        return callable_annotations.get('return', None) == return_type


    @classmethod
    def get_dependency_type(cls):
        return get_generic_type_args(cls, 0)

    def __init__(
            self,
            new_dependency_instance: Any,
            injector_target: Callable = None,
            *args,
            **kwargs
    ):
        super().__init__(injector_target=injector_target, *args, **kwargs)

        dependency_type = self.get_dependency_type()

        if not isinstance(new_dependency_instance, self.get_dependency_type()):
            raise TypeError(
                f'Invalid new_dependency_instance {dependency_type} -'
                f' must be an instance of {dependency_type}.'
            )

        self._new_dependency_instance = new_dependency_instance

    @classmethod
    def _find_callable_args_matching_dependency_type(
            cls,
            target_callable: Callable,
    ) -> list[str]:
        callable_annotations = get_type_hints(target_callable)
        target_type = cls.get_dependency_type()

        arg_matches = [
            arg_name
            for arg_name, arg_type in callable_annotations.items()
            if issubclass(arg_type, target_type)
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

        if not len(callable_args_matching_dependency_type) == 1:
            raise TypeError(
                f'Invalid target_callable {injector_target} - '
                f'must have exactly one parameter of type {self.get_dependency_type()}'
            )

        original_dependency_arg_name = callable_args_matching_dependency_type[0]

        return partial(injector_target, **{original_dependency_arg_name: self._new_dependency_instance})