from __future__ import annotations

import logging
import time

from typing import Callable, TypeVar


T = TypeVar('T')

logger = logging.getLogger(__name__)


def retry(
    fn: Callable[[], T],
    *,
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    if attempts < 1:
        msg = f'attempts must be >= 1, got {attempts}'
        raise ValueError(msg)

    last_exc: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except exceptions as exc:
            last_exc = exc

            if attempt == attempts:
                break

            wait = delay * (backoff ** (attempt - 1))

            logger.warning(
                'Attempt %d/%d failed: %s. Retrying in %.1fs',
                attempt,
                attempts,
                exc,
                wait,
            )

            time.sleep(wait)

    assert last_exc is not None
    raise last_exc
