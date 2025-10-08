from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.cache import cache

if TYPE_CHECKING:
    from typing import Any


class ProgressTracker:
    def __init__(self, key: str, timeout: int = 300) -> None:
        self.key = f'progress_tracker_{key}'
        self.timeout = timeout

    def update(
        self,
        step: str,
        message: str,
        progress: int,
        **kwargs: Any
    ) -> None:
        data = {
            'step': step,
            'message': message,
            'progress': progress,
            **kwargs
        }
        cache.set(self.key, data, timeout=self.timeout)

    def get(self) -> dict[str, Any] | None:
        return cache.get(self.key)

    def clear(self) -> None:
        cache.delete(self.key)

    def error(self, message: str) -> None:
        self.update('error', message, 0)
