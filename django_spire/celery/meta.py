import time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_ESTIMATED_TIME_BUFFER = 0.10


class CeleryTaskMeta(BaseModel):
    model_config = ConfigDict(extra='allow')

    progress: float | None = None
    start_time_seconds: float | None = None
    last_update_time_seconds: float | None = None
    estimated_end_time_seconds: float | None = None
    end_time_seconds: float | None = None
    _progress_updates_count: int = 0


    @property
    def estimated_progress(self) -> float | None:
        if self.progress and self.estimated_remaining_seconds:
            progress_per_second = (1.0 - self.progress) / self.estimated_remaining_seconds
            time_since_last_update_seconds = time.time() - self.last_update_time_seconds
            new_progress = progress_per_second * time_since_last_update_seconds

            return min(self.progress + new_progress, 1.0)

        return None

    @property
    def estimated_remaining_seconds(self) -> float | None:
        if self.estimated_end_time_seconds:
            return max(self.estimated_end_time_seconds - time.time(), 0.0)

        return None

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "progress" and isinstance(value, float):
            if self.start_time_seconds is None:
                self.start_time_seconds = time.time()

            if self._progress_updates_count >= 2:

                current_time_seconds = time.time()
                elapsed_seconds = current_time_seconds - self.start_time_seconds
                estimated_total_seconds = elapsed_seconds / value
                remaining_seconds = estimated_total_seconds - elapsed_seconds

                new_estimated_end_time_seconds = current_time_seconds + (
                        remaining_seconds * (_ESTIMATED_TIME_BUFFER + 1.0)
                )

                if self.estimated_end_time_seconds is None:
                    self.estimated_end_time_seconds = new_estimated_end_time_seconds

                else:
                    difference_seconds = self.estimated_end_time_seconds - new_estimated_end_time_seconds
                    change_threshold = _ESTIMATED_TIME_BUFFER * self.estimated_run_time_seconds

                    if abs(difference_seconds) > abs(change_threshold):
                        self.estimated_end_time_seconds = new_estimated_end_time_seconds

            else:
                self._progress_updates_count += 1

            self.last_update_time_seconds = time.time()

        super().__setattr__(name, value)

    @property
    def estimated_run_time_seconds(self) -> float | None:
        if self.start_time_seconds and self.estimated_end_time_seconds:
            return self.estimated_end_time_seconds - self.estimated_end_time_seconds

        return None

    @property
    def run_time_seconds(self) -> float | None:
        if self.start_time_seconds and self.end_time_seconds:
            return self.end_time_seconds - self.start_time_seconds

        return None
