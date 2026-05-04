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
_DELAY_MAX = 300.0


def retry(
    function: Callable[[], T],
    *,
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = _DEFAULT_EXCEPTIONS,
) -> T:
    if attempts < 1:
        message = f'The attempt(s) must be >= 1, got {attempts}'
        raise InvalidParameterError(message)

    if delay < 0.0:
        message = f'The delay must be non-negative, got {delay}'
        raise InvalidParameterError(message)

    if backoff < 1.0:
        message = f'The backoff must be >= 1.0, got {backoff}'
        raise InvalidParameterError(message)

    if not exceptions:
        message = 'The exception(s) tuple must not be empty'
        raise InvalidParameterError(message)

    last_exception: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return function()
        except exceptions as exception:
            last_exception = exception

            if attempt == attempts:
                break

            wait = min(
                delay * (backoff ** (attempt - 1)),
                _DELAY_MAX,
            )

            logger.warning(
                'Attempt %d/%d failed: %s. Retrying in %.1fs',
                attempt,
                attempts,
                exception,
                wait,
            )

            time.sleep(wait)

    message = (
        f'retry exhausted {attempts} attempt(s): '
        f'{last_exception}'
    )

    raise RetryExhaustedError(message) from last_exception
