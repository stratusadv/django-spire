from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.progress.tracker import ProgressTracker

if TYPE_CHECKING:
    from typing import Any

    from django_spire.contrib.progress.enums import ProgressStatus


class ProgressTrackingMixin:
    _tracker: ProgressTracker | None = None

    def get_tracker_key(self) -> str:
        raise NotImplementedError

    @property
    def tracker(self) -> ProgressTracker:
        if self._tracker is None:
            self._tracker = ProgressTracker(self.get_tracker_key())

        return self._tracker

    def progress_error(self, message: str) -> None:
        self.tracker.error(message)

    def update_progress(
        self,
        status: ProgressStatus,
        message: str,
        progress: int,
        **kwargs: Any
    ) -> None:
        self.tracker.update(status, message, progress, **kwargs)
