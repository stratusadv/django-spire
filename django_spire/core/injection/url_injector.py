import importlib
import sys
from types import FunctionType
from typing import Callable, Tuple, Union

from django.urls import path, URLResolver, URLPattern, include

from django_spire.core.injection.composite_injector import BaseCompositeInjector
from django_spire.core.injection.decorator_injector import DecoratorInjector
from django_spire.core.injection.dependency_injector import DependencyInjector

URLConf = Tuple[URLPattern | URLResolver, ...] | URLPattern | URLResolver


ALLOWED_URL_CHILD_INJECTOR_TYPES = (DecoratorInjector, DependencyInjector)


class UrlConfInjector(BaseCompositeInjector[URLConf]):
    allowed_child_injector_types = ALLOWED_URL_CHILD_INJECTOR_TYPES

    @staticmethod
    def _get_view_func_from_urlpattern(urlpattern: URLPattern) -> Callable:
        view_dotted_path_parts = urlpattern.lookup_str.split('.')
        view_module_str = '.'.join(view_dotted_path_parts[:-1])
        view_func_name = view_dotted_path_parts[-1]

        if view_module_str not in sys.modules:
            view_module = importlib.import_module(view_module_str)
        else:
            view_module = sys.modules[view_module_str]

        return getattr(view_module, view_func_name)

    def __init__(
            self,
            child_injectors: tuple[Union[ALLOWED_URL_CHILD_INJECTOR_TYPES], ...] = (),
            injector_target: URLConf = None,
            *args,
            **kwargs
    ):
        super().__init__(child_injectors, injector_target, *args, **kwargs)

    def _inject_url(self, url: URLPattern | URLResolver):
        if isinstance(url, URLPattern):
            return self._inject_url_pattern(url)
        elif isinstance(url, URLResolver):
            return self._inject_url_resolver(url)
        else:
            raise TypeError('All urls passed to add_urlpatterns must be '
                            'either URLPattern or URLResolver')

    def _inject_url_resolver(self, url_resolver: URLResolver):
        urlpatterns_for_resolver = [
            self._inject_url(url)
            for url in url_resolver.url_patterns
        ]

        return path(
            route=str(url_resolver.pattern),
            view=include((urlpatterns_for_resolver, url_resolver.app_name), namespace=url_resolver.namespace),
        )

    def _inject_url_pattern(self, url_pattern: URLPattern):
        view = self._get_view_func_from_urlpattern(url_pattern)
        if not isinstance(view, FunctionType):
            return url_pattern

        for injector in self._child_injectors.get(view, []):
            view = injector(view)

        for injector in self._child_injectors.get(None, []):
            view = injector(view)

        return path(
            route=str(url_pattern.pattern),
            view=view,
            name=url_pattern.name
        )

    def _inject(
            self,
            injector_target: URLConf = None,
            *args,
            **kwargs
    ) -> URLConf:
        if not isinstance(injector_target, tuple):
           injector_target = [injector_target]

        injected_urlpatterns = tuple([
            self._inject_url(url)
            for url in injector_target
        ])

        if len(injected_urlpatterns) == 1:
            return injected_urlpatterns[0]
        else:
            return injected_urlpatterns