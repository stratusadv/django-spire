from abc import ABC
from typing import Callable, Concatenate

from django.http import HttpRequest, HttpResponse

from django_spire.core.controllers.dependency_injection.view_dependency import \
    BaseViewDependency


class BaseAppModifier(ABC):
    target_app_names: list[str] = None
    view_dependencies_container: dict[BaseViewDependency, BaseViewDependency] = None
    view_decorators: dict[
        Callable[[Concatenate[HttpRequest, ...]], HttpResponse],
        list[Callable]
    ] = None
    url_conf_module = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.validate_attribute('target_app_names', list[str])

        if hasattr(cls, 'view_dependencies_container'):
            cls.validate_attribute(
                'view_dependencies_container',
                dict[BaseViewDependency, BaseViewDependency]
            )
        if hasattr(cls, 'view_decorators'):
            cls.validate_attribute(
                'view_decorators',
                dict[
                    Callable[[Concatenate[HttpRequest, ...]], HttpResponse],
                    list[Callable]
                ]
            )

    @classmethod
    def validate_attribute(cls, attribute_name: str, attribute_type: type) -> None:
        error =f'{cls} must have a valid "{attribute_name}" attribute of type "{attribute_type}"'

        if hasattr(cls, attribute_name):
            attr = getattr(cls, attribute_name)
            if not isinstance(attr, attribute_type):
                raise ValueError(error)
        else:
            raise ValueError(error)

    @classmethod
    def modify_view_kwargs(cls, view_kwargs: dict):
        for key, value in view_kwargs.items():
            if value in cls.view_dependencies_container:
                view_kwargs[key] = cls.view_dependencies_container[value]

    @classmethod
    def modify_view_decorators(cls, view_function: Callable):
        if cls.view_decorators.get(view_function, None) is not None:
            for decorator in cls.view_decorators[view_function]:
                view_function = decorator(view_function)
