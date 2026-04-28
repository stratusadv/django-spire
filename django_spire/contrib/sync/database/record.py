from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django_spire.contrib.sync.core.exceptions import RecordFieldError


@dataclass
class SyncRecord:
    key: str
    data: dict[str, Any]
    timestamps: dict[str, int]
    received_at: int = field(default=0, compare=False)

    @property
    def sync_field_last_modified(self) -> int:
        ts_max = max(self.timestamps.values()) if self.timestamps else 0
        return max(ts_max, self.received_at)

    @classmethod
    def from_dict(cls, key: str, data: dict[str, Any]) -> SyncRecord:
        record_data = data.get('data', {})
        record_timestamps = data.get('timestamps', {})

        if not isinstance(record_data, dict):
            message = f"Record {key!r}: 'data' must be a dict, got {type(record_data).__name__}"
            raise RecordFieldError(message)

        if not isinstance(record_timestamps, dict):
            message = f"Record {key!r}: 'timestamps' must be a dict, got {type(record_timestamps).__name__}"
            raise RecordFieldError(message)

        for ts_key, ts_value in record_timestamps.items():
            if not isinstance(ts_key, str):
                message = f"Record {key!r}: timestamp key {ts_key!r} must be a string"
                raise RecordFieldError(message)

            if not isinstance(ts_value, int) or isinstance(ts_value, bool):
                message = f"Record {key!r}: timestamp for {ts_key!r} must be an int, got {type(ts_value).__name__}"
                raise RecordFieldError(message)

        return cls(
            key=key,
            data=record_data,
            timestamps=record_timestamps,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'data': self.data,
            'timestamps': self.timestamps,
        }
