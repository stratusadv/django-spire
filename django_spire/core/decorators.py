from django.db import connections
from functools import wraps


def close_db_connections(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            connections.close_all()
    return inner
