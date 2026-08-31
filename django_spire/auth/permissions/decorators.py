from __future__ import annotations

import functools

from dataclasses import dataclass
from typing import Sequence, TYPE_CHECKING

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@dataclass(frozen=True)
class SpireGate:
    """
    A frozen record of the permission gate a decorator placed on a view.

    This record is stamped onto the decorator's wrapper as `__spire_gate__` so
    the permission matrix in `django_spire.testing.permissions` can read a
    route's declared gate without inspecting closures. The stamp lives in the
    wrapper's `__dict__`, and `functools.wraps` copies `__dict__` upward, so
    any wraps-using decorator stacked above the gate carries the stamp to the
    outermost wrapper on its own.

    :param all_required: Whether every permission is required, rather than any one.
    :param opaque: Whether the gate includes a callable check the matrix cannot predict.
    :param permissions: The declared permission labels in `app_label.codename` form.
    """

    all_required: bool
    opaque: bool
    permissions: tuple[str, ...]


def permission_required_decorator_function(
    permissions: str | Sequence[str],
    method,
    request: WSGIRequest,
    *args,
    all_required: bool = True,
    **kwargs,
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


def permission_required(*permissions: str, all_required: bool = True):
    """
    A decorator factory that gates a view behind Django permissions.

    An unauthenticated request is redirected to the login page, and an
    authenticated request without the declared permissions raises
    PermissionDenied.

    :param permissions: The permission labels in `app_label.codename` form.
    :param all_required: Whether every permission is required, rather than any one.
    :return: The decorator that wraps the view.
    """

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

        # The stamp is set after functools.wraps so a gate copied up from an
        # inner decorator is overwritten by this, the outermost, gate.
        wrapper.__spire_gate__ = SpireGate(
            all_required=all_required,
            opaque=False,
            permissions=tuple(permissions),
        )

        return wrapper

    return decorator
