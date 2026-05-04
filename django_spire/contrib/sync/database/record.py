from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django_spire.contrib.sync.core.exceptions import (
    InvalidParameterError,
    RecordFieldError,
)


@dataclass
class SyncRecord:
    key: str
    data: dict[str, Any]
    timestamps: dict[str, int]
    received_at: int = field(default=0, compare=False)

    def __post_init__(self) -> None:
        if self.key == '':
            message = 'SyncRecord key must be a non-empty string'
            raise InvalidParameterError(message)

        if self.received_at < 0:
            message = (
                f'received_at must be non-negative, '
                f'got {self.received_at}'
            )

            raise InvalidParameterError(message)

    @property
    def sync_field_last_modified(self) -> int:
        ts_max = (
            max(self.timestamps.values())
            if self.timestamps
            else 0
        )

        return max(ts_max, self.received_at)

    @classmethod
    def from_dict(cls, key: str, data: dict[str, Any]) -> SyncRecord:
        if key == '':
            message = 'SyncRecord key must be a non-empty string'
            raise RecordFieldError(message)

        record_data = data.get('data', {})
        record_timestamps = data.get('timestamps', {})
        record_received_at = data.get('received_at', 0)

        if not isinstance(record_data, dict):
            message = (
                f"Record {key!r}: 'data' must be a dict, "
                f'got {type(record_data).__name__}'
            )

            raise RecordFieldError(message)

        if not isinstance(record_timestamps, dict):
            message = (
                f"Record {key!r}: 'timestamps' must be a "
                f'dict, got {type(record_timestamps).__name__}'
            )

            raise RecordFieldError(message)

        if (
            not isinstance(record_received_at, int)
            or isinstance(record_received_at, bool)
        ):
            message = (
                f"Record {key!r}: 'received_at' must be an int, "
                f'got {type(record_received_at).__name__}'
            )

            raise RecordFieldError(message)

        if record_received_at < 0:
            message = (
                f"Record {key!r}: 'received_at' must be "
                f'non-negative, got {record_received_at}'
            )

            raise RecordFieldError(message)

        for ts_key, ts_value in record_timestamps.items():
            if not isinstance(ts_key, str):
                message = (
                    f'Record {key!r}: timestamp key '
                    f'{ts_key!r} must be a string'
                )

                raise RecordFieldError(message)

            if not isinstance(ts_value, int) or isinstance(ts_value, bool):
                message = (
                    f'Record {key!r}: timestamp for '
                    f'{ts_key!r} must be an int, '
                    f'got {type(ts_value).__name__}'
                )

                raise RecordFieldError(message)

            if ts_value < 0:
                message = (
                    f'Record {key!r}: timestamp for '
                    f'{ts_key!r} must be non-negative, '
                    f'got {ts_value}'
                )

                raise RecordFieldError(message)

        return cls(
            key=key,
            data=record_data,
            timestamps=record_timestamps,
            received_at=record_received_at,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'data': self.data,
            'timestamps': self.timestamps,
        }

