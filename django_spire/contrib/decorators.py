from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, Callable, ParamSpec, TypeVar

from django.conf import settings
from django.db import connections
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


P = ParamSpec('P')
T = TypeVar('T')


@dataclass(frozen=True)
class SpireRequest:
    """
    A frozen record of the request shape a decorator demands before the view runs.

    This record is stamped onto the decorator's wrapper as `__spire_request__`
    so the permission matrix in `django_spire.testing.permissions` can fire a
    request the decorator lets through, rather than one it answers itself
    before any permission gate below it runs. The stamp lives in the wrapper's
    `__dict__`, and `functools.wraps` copies `__dict__` upward, so any
    wraps-using decorator stacked above carries the stamp to the outermost
    wrapper on its own.

    :param content_type: The content type the decorator requires.
    :param method: The HTTP method the decorator requires.
    """

    content_type: str
    method: str


def access_key_required(setting_name: str, param_name: str = 'access_key') -> Callable[P, T]:
    def decorator(view: Callable[P, T]) -> Callable[P, T]:
        @wraps(view)
        def wrapper(request: WSGIRequest, *args, **kwargs) -> HttpResponse:
            key = getattr(settings, setting_name, None)

            if not key or str(kwargs.get(param_name)) != str(key):
                raise Http404

            return view(request, *args, **kwargs)

        return wrapper

    return decorator


def close_db_connections(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        finally:
            connections.close_all()

    return inner


def valid_ajax_request_required(method: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    @wraps(method)
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.method != 'POST' and request.content_type != 'application/json':
            return JsonResponse({'type': 'error', 'message': 'Invalid Request'})

        return method(request, *args, **kwargs)

    wrapper.__spire_request__ = SpireRequest(
        content_type='application/json',
        method='POST',
    )

    return wrapper
