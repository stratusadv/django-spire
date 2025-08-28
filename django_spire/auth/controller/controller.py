import functools

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.urls import reverse

from django_spire.auth.group.decorators import permission_required_decorator_function


class BaseAuthController:
    def __init__(self, request: WSGIRequest | None = None):
        self.request: WSGIRequest | None = None

    def permission_required(self, permissions: str | tuple[str, ...]):
        if isinstance(permissions, str):
            permissions = (permissions,)

        def decorator(method):
            @functools.wraps(method)
            def wrapper(request: WSGIRequest, *args, **kwargs):
                self.request = request

                if self.request is None:
                    raise Exception('AuthController.request is None')


                uncallable_permissions = []

                for permission in permissions:
                    callable_permission = getattr(self, permission)
                    if callable(callable_permission):
                        if not callable_permission():
                            return HttpResponseRedirect(
                                reverse('django_spire:auth:admin:login')
                            )
                    else:
                        uncallable_permissions.append(permission)

                return permission_required_decorator_function(
                    permissions,
                    method,
                    request,
                    *args,
                    **kwargs
                )

            return wrapper

        return decorator


class AuthController:
    def __new__(cls, controller: str, **kwargs):
        from django.conf import settings
        from importlib import import_module

        if controller not in settings.AUTH_CONTROLLERS:
            raise Exception(f'Controller {controller} not found in settings.AUTH_CONTROLLERS')

        module_path = '.'.join(settings.AUTH_CONTROLLERS[controller].split('.')[0:-1])
        print(module_path)

        try:
            import_module(module_path)
            module = import_module(module_path)

            return getattr(module, settings.AUTH_CONTROLLERS[controller].split('.')[-1])()

        except ModuleNotFoundError:
            return BaseAuthController()
