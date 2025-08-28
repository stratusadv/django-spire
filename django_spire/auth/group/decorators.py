from __future__ import annotations

import functools

from typing_extensions import TYPE_CHECKING

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def permission_required_decorator_function(
        permissions,
        method,
        request: WSGIRequest,
        *args,
        **kwargs
):
    if request.user.is_authenticated:
        if isinstance(permissions, str):
            perms = (permissions,)
        else:
            perms = permissions

        if not request.user.has_perms(perms):
            raise PermissionDenied

        return method(request, *args, **kwargs)

    return HttpResponseRedirect(reverse('django_spire:auth:admin:login'))


def permission_required(permissions: str | tuple[str, ...]):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(request: WSGIRequest, *args, **kwargs):
            return permission_required_decorator_function(
                permissions,
                method,
                request,
                *args,
                **kwargs
            )

        return wrapper

    return decorator
