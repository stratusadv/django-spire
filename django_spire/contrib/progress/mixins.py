from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.progress.tracker import ProgressTracker

if TYPE_CHECKING:
    from typing import Any


class ProgressTrackingMixin:
    _tracker: ProgressTracker | None = None

    def get_tracker_key(self) -> str:
        raise NotImplementedError

    @property
    def tracker(self) -> ProgressTracker:
        if self._tracker is None:
            key = self.get_tracker_key()
            self._tracker = ProgressTracker(key)

        return self._tracker

    def update_progress(
        self,
        step: str,
        message: str,
        progress: int,
        **kwargs: Any
    ) -> None:
        self.tracker.update(step, message, progress, **kwargs)

    def progress_error(self, message: str) -> None:
        self.tracker.error(message)
