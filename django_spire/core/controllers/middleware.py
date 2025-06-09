from __future__ import annotations

import importlib
from collections import defaultdict
from typing import Callable, Concatenate

from django.apps import apps
from django.http import HttpRequest, HttpResponse
from typing_extensions import TYPE_CHECKING
from django.conf import settings

from django_spire.core.controllers.dependency_injection.view_dependency import \
    BaseViewDependency
from django_spire.core.controllers.options import BaseAppModifier

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

MODIFIERS_MODULE_NAME = 'mods'

class AppModifierMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.app_modifiers: dict[
            str,
            type[BaseAppModifier]
        ] = {}

        for appconfig in apps.get_app_configs():
            try:
                modifiers_module = importlib.import_module(f'{appconfig.module.__name__}.{MODIFIERS_MODULE_NAME}')
            except ImportError:
                pass
            else:
                for attr_str in dir(modifiers_module):
                    attr = getattr(modifiers_module, attr_str)

                    if not isinstance(attr, type):
                        continue

                    if issubclass(attr, BaseAppModifier):
                        for app_name in attr.target_app_names:
                            self.app_modifiers[app_name] = attr

    def __call__(self, request: WSGIRequest):
        foo = settings.ROOT_URLCONF

        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        for name in request.resolver_match.app_names:
            if name in self.app_modifiers:
                modifier = self.app_modifiers[name]
                modifier.modify_view_kwargs(view_kwargs)
                modifier.modify_view_decorators(view_func)

                return None

        return None