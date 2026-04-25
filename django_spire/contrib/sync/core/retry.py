from __future__ import annotations

import logging
import time

from typing import Callable, TypeVar

from django_spire.contrib.sync.core.exceptions import (
    InvalidParameterError,
    RetryExhaustedError,
)


T = TypeVar('T')

logger = logging.getLogger(__name__)

_DEFAULT_EXCEPTIONS: tuple[type[Exception], ...] = (OSError, TimeoutError)


def retry(
    function: Callable[[], T],
    *,
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = _DEFAULT_EXCEPTIONS,
) -> T:
    if attempts < 1:
        message = f'attempts must be >= 1, got {attempts}'
        raise InvalidParameterError(message)

    last_exception: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return function()
        except exceptions as exception:
            last_exception = exception

            if attempt == attempts:
                break

            wait = delay * (backoff ** (attempt - 1))

            logger.warning(
                'Attempt %d/%d failed: %s. Retrying in %.1fs',
                attempt,
                attempts,
                exception,
                wait,
            )

            time.sleep(wait)

    message = f'retry exhausted {attempts} attempt(s): {last_exception}'
    raise RetryExhaustedError(message) from last_exception
