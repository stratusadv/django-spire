from __future__ import annotations

import functools

from typing import TYPE_CHECKING

from django.core.exceptions import PermissionDenied

from django_spire.auth.controller.exceptions import (
    AuthControllerNotFoundError,
    AuthControllerRequestError,
)
from django_spire.auth.permissions.decorators import (
    permission_required_decorator_function,
    SpireGate,
)
from django_spire.conf import settings
from django_spire.contrib.utils import get_object_from_module_string

if TYPE_CHECKING:
    from typing import Any, Callable

    from django.core.handlers.wsgi import WSGIRequest


class BaseAuthController:
    def __init__(self, request: WSGIRequest | None = None) -> None:
        self._request = request

    @property
    def request(self) -> WSGIRequest:
        if self._request is None:
            message = 'AuthController.request is None'
            raise AuthControllerRequestError(message)

        return self._request

    @request.setter
    def request(self, value: WSGIRequest) -> None:
        self._request = value

    def permission_required(self, *permissions: str, all_required: bool = True) -> Callable:
        def decorator(method: Callable[..., Any]) -> Callable:
            @functools.wraps(method)
            def wrapper(request: WSGIRequest, *args, **kwargs) -> Callable:
                self.request = request

                uncallable_permissions = []

                for perm in permissions:
                    callable_permission = getattr(self, perm) if hasattr(self, perm) else perm

                    if callable(callable_permission):
                        if not all_required and callable_permission():
                            return method(request, *args, **kwargs)

                        if not callable_permission():
                            raise PermissionDenied

                    else:
                        uncallable_permissions.append(perm)

                return permission_required_decorator_function(
                    uncallable_permissions,
                    method,
                    self.request,
                    *args,
                    all_required=all_required,
                    **kwargs,
                )

            # A permission naming a callable on this controller is classified
            # at decoration time: the controller instance already exists when
            # its permission_required method runs, so getattr resolves the
            # same attribute the wrapper will call per request. A callable
            # check marks the gate as a custom check because its outcome cannot be
            # predicted from permission labels alone.
            permissions_callable = tuple(
                permission
                for permission in permissions
                if callable(getattr(self, permission, None))
            )

            permissions_label = tuple(
                permission
                for permission in permissions
                if permission not in permissions_callable
            )

            wrapper.__spire_gate__ = SpireGate(
                all_required=all_required,
                has_custom_check=bool(permissions_callable),
                permissions=permissions_label,
            )

            return wrapper

        return decorator


class AppAuthController:
    def __new__(
        cls, app_name: str, request: WSGIRequest | None = None, **kwargs: dict[str, Any]
    ) -> BaseAuthController:
        if app_name not in settings.DJANGO_SPIRE_AUTH_CONTROLLERS:
            message = f'Controller {app_name} not found in settings.AUTH_CONTROLLERS'
            raise AuthControllerNotFoundError(message)

        try:
            return get_object_from_module_string(settings.DJANGO_SPIRE_AUTH_CONTROLLERS[app_name])(
                request
            )
        except ModuleNotFoundError as err:
            message = f'Auth Controller for {app_name} not found'
            raise AuthControllerNotFoundError(message) from err
