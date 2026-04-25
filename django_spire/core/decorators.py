from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Callable, ParamSpec, TypeVar

from django.conf import settings
from django.db import connections
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


P = ParamSpec('P')
T = TypeVar('T')


def access_key_required(
    setting_name: str,
    param_name: str = 'access_key',
) -> Callable[P, T]:
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


def valid_ajax_request_required(
    method: Callable[..., HttpResponse]
) -> Callable[..., HttpResponse]:
    @wraps(method)
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.method != 'POST' and request.content_type != 'application/json':
            return JsonResponse(
                {'type': 'error', 'message': 'Invalid Request'}
            )

        return method(request, *args, **kwargs)

    return wrapper
