import time
from datetime import datetime, UTC
    from typing import Any, Callable, Generic, Self, TypeVar

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

_ESTIMATED_TIME_BUFFER = 0.10

# The native tracer's terminal write (mark_as_done / mark_as_failure / mark_as_retry)
# overwrites the main backend row and destroys the last mid-run meta, so the tracker
# writes its final meta to this derived row, which the web reads on the terminal
# transition. A separate row means no collision with the terminal write.
FINAL_META_KEY_SUFFIX = ':spire-final-meta'


def derive_final_meta_key(task_id: str) -> str:
    return f'{task_id}{FINAL_META_KEY_SUFFIX}'


DataT = TypeVar('DataT')


class CeleryTaskMeta(BaseModel, Generic[DataT]):
    model_config = ConfigDict(extra='allow')

    data: DataT = Field(default_factory=dict)
    progress: float | None = None
    started_time: float | None = None
    last_update_time: float | None = None
    estimated_completed_time: float | None = None
    completed_time: float | None = None
    retries: int = 0
    error: str | None = None
    error_traceback: str | None = None
    failed_time: float | None = None
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
    def estimated_remaining_seconds(self) -> float | int | None:
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
            return self.estimated_completed_time - self.started_time

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

    def set_failed(self, error: str) -> None:
        self.error = error
        self.failed_time = time.time()

    def set_started(self) -> None:
        self.progress = 0.02
        self.started_time = time.time()

    def set_started_and_completing_soon(self) -> None:
        self.set_started()
        self.progress = 1.0
        self.estimated_completed_time = time.time() + 5
        self.last_update_time = time.time()

    @staticmethod
    def _deep_merge_data(base: dict, other: dict) -> dict:
        merged = {**base}

        for key, value in other.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = CeleryTaskMeta._deep_merge_data(merged[key], value)
            else:
                merged[key] = value

        return merged

    def merge(self, other: Self) -> Self:
        for field, value in other.model_dump().items():
            if value is None:
                continue

            if field == 'data':
                value = self._deep_merge_data(self.data, value)

            if field in type(self).model_fields:
                object.__setattr__(self, field, value)
            else:
                if self.__pydantic_extra__ is None:
                    self.__pydantic_extra__ = {}

                self.__pydantic_extra__[field] = value

        return self


class TaskDataModel(BaseModel):
    model_config = ConfigDict(extra='allow', validate_assignment=True)

    _on_change: Callable[[], None] | None = PrivateAttr(default=None)

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)

        hook = self._on_change
        if name != '_on_change' and hook is not None:
            hook()
