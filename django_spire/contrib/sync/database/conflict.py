from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol

from django_spire.contrib.sync.core.exceptions import ConflictStateError
from django_spire.contrib.sync.database.record import SyncRecord


META_FIELDS = frozenset({'sync_field_timestamps', 'sync_field_last_modified'})


class ConflictType(StrEnum):
    BOTH_MODIFIED = 'both_modified'
    COMPATIBLE = 'compatible'
    DELETE_VS_MODIFY = 'delete_vs_modify'
    MODIFY_VS_DELETE = 'modify_vs_delete'


class ResolutionSource(StrEnum):
    LOCAL = 'local'
    MERGED = 'merged'
    REMOTE = 'remote'


@dataclass
class FieldConflict:
    field_name: str
    local_value: Any
    remote_value: Any
    local_timestamp: int
    remote_timestamp: int


@dataclass
class RecordConflict:
    key: str
    model_label: str
    conflict_type: ConflictType
    field_conflicts: list[FieldConflict] = field(default_factory=list)
    local: SyncRecord | None = None
    remote: SyncRecord | None = None


@dataclass
class RecordResolution:
    record: SyncRecord | None
    source: ResolutionSource
    delete: bool = False
    field_conflicts: list[FieldConflict] = field(default_factory=list)


class ConflictResolver(Protocol):
    def resolve(self, conflict: RecordConflict) -> RecordResolution: ...


def _require_both(conflict: RecordConflict) -> tuple[SyncRecord, SyncRecord]:
    return _require_local(conflict), _require_remote(conflict)


def _require_local(conflict: RecordConflict) -> SyncRecord:
    if conflict.local is None:
        message = (
            f'conflict.local must not be None '
            f'for {conflict.conflict_type} on key {conflict.key!r}'
        )

        raise ConflictStateError(message)

    return conflict.local


def _require_remote(conflict: RecordConflict) -> SyncRecord:
    if conflict.remote is None:
        message = (
            f'conflict.remote must not be None '
            f'for {conflict.conflict_type} on key {conflict.key!r}'
        )

        raise ConflictStateError(message)

    return conflict.remote


class FieldOwnershipWins:
    def __init__(
        self,
        local_fields: set[str],
        remote_fields: set[str],
        exclude_fields: set[str] | None = None,
        prefer_remote_on_tie: bool = False,
    ) -> None:
        self._exclude = (exclude_fields or set()) | META_FIELDS
        self._local_fields = local_fields
        self._prefer_remote_on_tie = prefer_remote_on_tie
        self._remote_fields = remote_fields

    def resolve(self, conflict: RecordConflict) -> RecordResolution:
        if conflict.conflict_type == ConflictType.DELETE_VS_MODIFY:
            return RecordResolution(
                record=_require_local(conflict),
                source=ResolutionSource.LOCAL,
            )

        if conflict.conflict_type == ConflictType.MODIFY_VS_DELETE:
            return RecordResolution(
                record=_require_remote(conflict),
                source=ResolutionSource.REMOTE,
            )

        local, remote = _require_both(conflict)

        local_data = local.data
        remote_data = remote.data
        local_timestamps = local.timestamps
        remote_timestamps = remote.timestamps

        all_fields = (set(local_data) | set(remote_data)) - self._exclude

        data: dict[str, Any] = {}
        timestamps: dict[str, int] = {}

        for field_name in sorted(all_fields):
            local_timestamp = local_timestamps.get(field_name, 0)
            remote_timestamp = remote_timestamps.get(field_name, 0)

            if field_name in self._local_fields:
                data[field_name] = local_data.get(field_name)
                timestamps[field_name] = local_timestamp
            elif field_name in self._remote_fields:  # noqa: SIM114
                data[field_name] = remote_data.get(field_name)
                timestamps[field_name] = remote_timestamp
            elif (
                remote_timestamp > local_timestamp
                or (
                    remote_timestamp == local_timestamp
                    and self._prefer_remote_on_tie
                )
            ):
                data[field_name] = remote_data.get(field_name)
                timestamps[field_name] = remote_timestamp
            else:
                data[field_name] = local_data.get(field_name)
                timestamps[field_name] = local_timestamp

        return RecordResolution(
            record=SyncRecord(
                key=conflict.key,
                data=data,
                timestamps=timestamps,
            ),
            source=ResolutionSource.MERGED,
            field_conflicts=conflict.field_conflicts,
        )


class FieldTimestampWins:
    def __init__(
        self,
        exclude_fields: set[str] | None = None,
        prefer_remote_on_tie: bool = False,
    ) -> None:
        self._exclude = (exclude_fields or set()) | META_FIELDS
        self._prefer_remote_on_tie = prefer_remote_on_tie

    def resolve(self, conflict: RecordConflict) -> RecordResolution:
        if conflict.conflict_type == ConflictType.DELETE_VS_MODIFY:
            return RecordResolution(
                record=_require_local(conflict),
                source=ResolutionSource.LOCAL,
            )

        if conflict.conflict_type == ConflictType.MODIFY_VS_DELETE:
            return RecordResolution(
                record=_require_remote(conflict),
                source=ResolutionSource.REMOTE,
            )

        local, remote = _require_both(conflict)

        local_data = local.data
        remote_data = remote.data
        local_timestamps = local.timestamps
        remote_timestamps = remote.timestamps

        all_fields = (set(local_data) | set(remote_data)) - self._exclude

        data: dict[str, Any] = {}
        timestamps: dict[str, int] = {}

        for field_name in sorted(all_fields):
            local_timestamp = local_timestamps.get(field_name, 0)
            remote_timestamp = remote_timestamps.get(field_name, 0)

            if (
                remote_timestamp > local_timestamp
                or (
                    remote_timestamp == local_timestamp
                    and self._prefer_remote_on_tie
                )
            ):
                data[field_name] = remote_data.get(field_name)
                timestamps[field_name] = remote_timestamp
            else:
                data[field_name] = local_data.get(field_name)
                timestamps[field_name] = local_timestamp

        return RecordResolution(
            record=SyncRecord(
                key=conflict.key,
                data=data,
                timestamps=timestamps,
            ),
            source=ResolutionSource.MERGED,
            field_conflicts=conflict.field_conflicts,
        )


class LocalWins:
    def resolve(self, conflict: RecordConflict) -> RecordResolution:
        if conflict.conflict_type == ConflictType.MODIFY_VS_DELETE:
            return RecordResolution(
                record=None,
                source=ResolutionSource.LOCAL,
                delete=True,
            )

        return RecordResolution(
            record=_require_local(conflict),
            source=ResolutionSource.LOCAL,
            field_conflicts=conflict.field_conflicts,
        )


class RemoteWins:
    def resolve(self, conflict: RecordConflict) -> RecordResolution:
        if conflict.conflict_type == ConflictType.DELETE_VS_MODIFY:
            return RecordResolution(
                record=None,
                source=ResolutionSource.REMOTE,
                delete=True,
            )

        return RecordResolution(
            record=_require_remote(conflict),
            source=ResolutionSource.REMOTE,
            field_conflicts=conflict.field_conflicts,
        )
