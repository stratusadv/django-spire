import logging
import time

from django.conf import settings


def performance_timer(func):
    def wrapper(*args, **kwargs):
        if settings.DEBUG:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()

            logging.warning(f'{end_time - start_time:.4f} seconds runtime for "{func.__module__}.{func.__qualname__}"')

            return result

        else:
            return func(*args, **kwargs)

    return wrapper