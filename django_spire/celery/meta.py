import time
from datetime import datetime, UTC
from typing import Any

from pydantic import BaseModel, ConfigDict

_ESTIMATED_TIME_BUFFER = 0.10


class CeleryTaskMeta(BaseModel):
    model_config = ConfigDict(extra='allow')

    progress: float | None = None
    started_time: float | None = None
    last_update_time: float | None = None
    estimated_completed_time: float | None = None
    completed_time: float | None = None
    _progress_updates_count: int = 0

    @property
    def completed_datetime(self) -> datetime | None:
        if self.completed_time:
            return datetime.fromtimestamp(self.completed_time, tz=UTC)

        return None

    @property
    def estimated_progress(self) -> float | None:
        if self.progress and self.estimated_remaining_seconds:
            time_since_last_update_seconds = time.time() - self.last_update_time
            new_progress = self.estimated_progress_per_second * time_since_last_update_seconds

            return min(self.progress + new_progress, 1.0)

        return None

    @property
    def estimated_progress_per_second(self) -> float:
        if self.progress and self.estimated_remaining_seconds:
            return (1.0 - self.progress) / self.estimated_remaining_seconds

        return 0.001

    @property
    def estimated_remaining_seconds(self) -> float | None:
        if self.estimated_completed_time:
            return max(self.estimated_completed_time - time.time(), 0.0)

        return None

    def __setattr__(self, name: str, value: Any) -> None:
        if name == 'progress' and isinstance(value, float):
            if self.started_time is None:
                self.started_time = time.time()

            if self._progress_updates_count >= 2:
                current_time = time.time()
                elapsed_seconds = current_time - self.started_time
                estimated_total_seconds = elapsed_seconds / value
                remaining_seconds = estimated_total_seconds - elapsed_seconds

                new_estimated_end_time_seconds = current_time + (
                    remaining_seconds * (_ESTIMATED_TIME_BUFFER + 1.0)
                )

                if self.estimated_completed_time is None:
                    self.estimated_completed_time = new_estimated_end_time_seconds

                else:
                    difference_seconds = (
                        self.estimated_completed_time - new_estimated_end_time_seconds
                    )
                    change_threshold = _ESTIMATED_TIME_BUFFER * self.estimated_run_time_seconds

                    if abs(difference_seconds) > abs(change_threshold):
                        self.estimated_completed_time = new_estimated_end_time_seconds

            else:
                self._progress_updates_count += 1

            self.last_update_time = time.time()

        super().__setattr__(name, value)

    @property
    def estimated_run_time_seconds(self) -> float | None:
        if self.started_time and self.estimated_completed_time:
            return self.estimated_completed_time - self.estimated_completed_time

        return None

    @property
    def run_time_seconds(self) -> float | None:
        if self.started_time and self.completed_time:
            return self.completed_time - self.started_time

        return None

    @property
    def started_datetime(self) -> datetime | None:
        if self.started_time:
            return datetime.fromtimestamp(self.started_time, tz=UTC)

        return None

    def set_completed(self) -> None:
        self.progress = 1.0
        self.completed_time = time.time()

    def set_started(self) -> None:
        self.progress = 0.02
        self.started_time = time.time()

    def set_started_and_completing_soon(self) -> None:
        self.set_started()
        self.progress = 1.0
        self.estimated_completed_time = time.time() + 5
        self.last_update_time = time.time() + 1
