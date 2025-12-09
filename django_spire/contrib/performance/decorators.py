from __future__ import annotations

import logging
import time

from typing import Callable, ParamSpec, TypeVar

from django.conf import settings


P = ParamSpec('P')
R = TypeVar('R')


def performance_timer(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if settings.DEBUG:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()

            message = f'{end_time - start_time:.4f} seconds runtime for "{func.__module__}.{func.__qualname__}"'
            logging.warning(message)

            return result

        return func(*args, **kwargs)

    return wrapper
