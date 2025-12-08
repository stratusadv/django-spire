from __future__ import annotations

from functools import wraps

from typing_extensions import Callable, ParamSpec, TypeVar

from django.db import connections
from django.http import HttpRequest, HttpResponse, JsonResponse


P = ParamSpec('P')
T = TypeVar('T')


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
