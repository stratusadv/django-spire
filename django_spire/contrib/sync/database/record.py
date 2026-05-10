from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

from django_spire.contrib.sync.core.exceptions import (
    InvalidParameterError,
    RecordFieldError,
)

if TYPE_CHECKING:
    from django_spire.contrib.sync.django.mixin import SyncableMixin


def _coerce_int(value: Any, label: str, record_key: str) -> int:
    if isinstance(value, bool):
        message = (
            f'Record {record_key!r}: {label} must be an int, '
            f'got bool'
        )

        raise RecordFieldError(message)

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    message = (
        f'Record {record_key!r}: {label} must be an int, '
        f'got {type(value).__name__}'
    )

    raise RecordFieldError(message)


@dataclass
class SyncRecord:
    key: str
    data: dict[str, Any]
    timestamps: dict[str, int]
    sequence: int = field(default=0, compare=False)
    origin_node: str = field(default='', compare=False)
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

        if self.sequence < 0:
            message = (
                f'sequence must be non-negative, '
                f'got {self.sequence}'
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
        record_sequence = data.get('sequence', 0)
        record_origin_node = data.get('origin_node', '')

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

        record_received_at = _coerce_int(
            record_received_at,
            "'received_at'",
            key,
        )

        if record_received_at < 0:
            message = (
                f"Record {key!r}: 'received_at' must be "
                f'non-negative, got {record_received_at}'
            )

            raise RecordFieldError(message)

        record_sequence = _coerce_int(
            record_sequence,
            "'sequence'",
            key,
        )

        if record_sequence < 0:
            message = (
                f"Record {key!r}: 'sequence' must be "
                f'non-negative, got {record_sequence}'
            )

            raise RecordFieldError(message)

        if not isinstance(record_origin_node, str):
            message = (
                f"Record {key!r}: 'origin_node' must be a string, "
                f'got {type(record_origin_node).__name__}'
            )

            raise RecordFieldError(message)

        sanitized_timestamps: dict[str, int] = {}

        for ts_key, ts_value in record_timestamps.items():
            if not isinstance(ts_key, str):
                message = (
                    f'Record {key!r}: timestamp key '
                    f'{ts_key!r} must be a string'
                )

                raise RecordFieldError(message)

            coerced = _coerce_int(
                ts_value,
                f'timestamp for {ts_key!r}',
                key,
            )

            if coerced < 0:
                message = (
                    f'Record {key!r}: timestamp for '
                    f'{ts_key!r} must be non-negative, '
                    f'got {coerced}'
                )

                raise RecordFieldError(message)

            sanitized_timestamps[ts_key] = coerced

        return cls(
            key=key,
            data=record_data,
            timestamps=sanitized_timestamps,
            sequence=record_sequence,
            origin_node=record_origin_node,
            received_at=record_received_at,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'data': self.data,
            'origin_node': self.origin_node,
            'sequence': self.sequence,
            'timestamps': self.timestamps,
        }


@dataclass(frozen=True)
class RecordContext:
    model: type[SyncableMixin]
    key: str
    sync_record: SyncRecord
    field_data: dict[str, Any]
    sequence: int
    origin_node: str
