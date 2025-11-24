from __future__ import annotations

import functools

from typing import Sequence, TYPE_CHECKING

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def permission_required_decorator_function(
        permissions: str | Sequence[str],
        method,
        request: WSGIRequest,
        *args,
        all_required: bool = True,
        **kwargs
):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('django_spire:auth:admin:login'))

    if isinstance(permissions, str):
        perms = (permissions,)
    else:
        perms = permissions

    if not all_required:
        for perm in perms:
            if request.user.has_perm(perm):
                return method(request, *args, **kwargs)

    if not request.user.has_perms(perms):
        raise PermissionDenied

    return method(request, *args, **kwargs)


def permission_required(
        *permissions: str,
        all_required: bool = True
):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(request: WSGIRequest, *args, **kwargs):
            return permission_required_decorator_function(
                permissions,
                method,
                request,
                *args,
                all_required=all_required,
                **kwargs
            )

        return wrapper

    return decorator
