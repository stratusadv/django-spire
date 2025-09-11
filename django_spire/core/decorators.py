from django.db import connections
from functools import wraps

from django.http import JsonResponse


def close_db_connections(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            connections.close_all()
    return inner


def valid_ajax_request_required(method):
    @wraps(method)
    def wrapper(request, *args, **kwargs):
        if request.method != 'POST' and request.content_type != 'application/json':
            return JsonResponse(
                {'type': 'error', 'message': 'Invalid Request'}
            )
        return method(request, *args, **kwargs)
    return wrapper
