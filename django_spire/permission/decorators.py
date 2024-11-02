import functools

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse


def permission_required(permissions: str | tuple[str]):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                if isinstance(permissions, str):
                    perms = (permissions,)
                else:
                    perms = permissions

                if not request.user.has_perms(perms):
                    raise PermissionDenied

                return method(request, *args, **kwargs)

            return HttpResponseRedirect(reverse('config_registration:login_redirect'))

        return wrapper

    return decorator
