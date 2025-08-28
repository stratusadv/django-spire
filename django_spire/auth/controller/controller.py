import functools

from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest

from django_spire.auth.group.decorators import permission_required_decorator_function
from django_spire.core.utils import get_object_from_module_string


class BaseAuthController:
    def __init__(
            self,
            request: WSGIRequest | None = None
    ):
        self._request = request

    @property
    def request(self):
        if self._request is None:
            raise Exception('AuthController.request is None')

        return self._request

    @request.setter
    def request(self, value: WSGIRequest):
        self._request = value

    def permission_required(
            self,
            *permissions: str,
            all_required: bool = True
    ):

        def decorator(method):
            @functools.wraps(method)
            def wrapper(request: WSGIRequest, *args, **kwargs):
                self.request = request

                uncallable_permissions = []

                for perm in permissions:
                    callable_permission = getattr(self, perm)
                    if callable(callable_permission):
                        if not all_required and callable_permission():
                            return method(request, *args, **kwargs)
                        elif not callable_permission():
                            raise PermissionDenied

                    else:
                        uncallable_permissions.append(perm)

                return permission_required_decorator_function(
                    uncallable_permissions,
                    method,
                    self.request,
                    *args,
                    all_required=all_required,
                    **kwargs
                )

            return wrapper

        return decorator


class AppAuthController:
    def __new__(
            cls,
            app_name: str,
            request: WSGIRequest | None = None,
            **kwargs
    ):
        from django_spire.conf import settings

        if app_name not in settings.DJANGO_SPIRE_AUTH_CONTROLLERS:
            raise Exception(f'Controller {app_name} not found in settings.AUTH_CONTROLLERS')

        try:
            return get_object_from_module_string(settings.DJANGO_SPIRE_AUTH_CONTROLLERS[app_name])(request)

        except ModuleNotFoundError:
            raise Exception(f'Auth Controller for {app_name} not found')
