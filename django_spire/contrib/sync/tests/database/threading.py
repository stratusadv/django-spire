from __future__ import annotations

from typing import Any, TYPE_CHECKING

from django_spire.contrib.sync.tests.django.helpers import close_connections

if TYPE_CHECKING:

    import threading
    from collections.abc import Callable


def thread_safe(
    target: Callable[..., Any],
    errors: list[Exception],
    barrier: threading.Barrier | None = None,
    barrier_timeout: float = 5.0,
) -> Callable[..., None]:
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            if barrier is not None:
                barrier.wait(timeout=barrier_timeout)

            target(*args, **kwargs)
        except Exception as exc:
            errors.append(exc)
        finally:
            close_connections()

    return wrapper
