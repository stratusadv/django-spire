from __future__ import annotations

import functools

from typing_extensions import TYPE_CHECKING

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def permission_required(permissions: str | tuple[str, ...]) -> callable:
    def decorator(method: callable) -> callable:
        @functools.wraps(method)
        def wrapper(request: WSGIRequest, *args, **kwargs) -> callable | HttpResponseRedirect:
            if request.user.is_authenticated:
                if isinstance(permissions, str):
                    perms = (permissions,)
                else:
                    perms = permissions

                if not request.user.has_perms(perms):
                    raise PermissionDenied

                return method(request, *args, **kwargs)

            return HttpResponseRedirect(reverse('auth:admin:login'))

        return wrapper

    return decorator
