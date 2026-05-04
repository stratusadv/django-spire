from __future__ import annotations

import logging

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from django_spire.contrib.sync.core.exceptions import InvalidParameterError
from django_spire.contrib.sync.core.model import Error
from django_spire.contrib.sync.database.conflict import (
    ConflictResolver,
    ConflictType,
    FieldConflict,
    FieldTimestampWins,
    META_FIELDS,
    RecordConflict,
)
from django_spire.contrib.sync.database.manifest import ConflictEntry

if TYPE_CHECKING:
    from django_spire.contrib.sync.database.manifest import ModelPayload
    from django_spire.contrib.sync.database.record import SyncRecord


logger = logging.getLogger(__name__)


@dataclass
class ReconciliationResult:
    applied_keys: set[str] = field(default_factory=set)
    compatible_keys: list[str] = field(default_factory=list)
    conflict_keys: list[str] = field(default_factory=list)
    conflict_log: list[ConflictEntry] = field(
        default_factory=list,
    )
    created_keys: set[str] = field(default_factory=set)
    errors: list[Error] = field(default_factory=list)
    response_records: dict[str, SyncRecord] = field(
        default_factory=dict,
    )
    to_delete: dict[str, int] = field(default_factory=dict)
    to_upsert: dict[str, SyncRecord] = field(
        default_factory=dict,
    )


class PayloadReconciler:
    def __init__(
        self,
        resolver: ConflictResolver | None = None,
    ) -> None:
        self._resolver = resolver or FieldTimestampWins()

    def _classify_deletes(
        self,
        payload: ModelPayload,
        local_records: dict[str, SyncRecord],
        result: ReconciliationResult,
    ) -> None:
        for key, tombstone_ts in payload.deletes.items():
            if key not in local_records:
                continue

            local = local_records[key]

            if local.sync_field_last_modified <= tombstone_ts:
                result.to_delete[key] = tombstone_ts
                continue

            conflict = RecordConflict(
                key=key,
                model_label=payload.model_label,
                conflict_type=ConflictType.DELETE_VS_MODIFY,
                local=local,
            )

            try:
                resolution = self._resolver.resolve(conflict)
            except Exception as exception:
                result.errors.append(Error(
                    key=key,
                    message=(
                        f'Delete conflict resolution failed: '
                        f'{exception}'
                    ),
                    exception=exception,
                ))

                continue

            if resolution.delete:
                result.to_delete[key] = tombstone_ts
            elif resolution.record is not None:
                result.response_records[key] = resolution.record
                result.conflict_keys.append(key)
            else:
                logger.warning(
                    'Delete conflict for %s:%s resolved '
                    'with no action (delete=False, record=None)',
                    payload.model_label,
                    key,
                )

    def _classify_record(
        self,
        key: str,
        remote: SyncRecord,
        model_label: str,
        local_records: dict[str, SyncRecord],
        checkpoint: int,
        result: ReconciliationResult,
    ) -> None:
        if key not in local_records:
            result.to_upsert[key] = remote
            result.created_keys.add(key)

            return

        local = local_records[key]

        if local.sync_field_last_modified <= checkpoint:
            result.to_upsert[key] = remote
            result.applied_keys.add(key)

            return

        self._resolve_conflict(
            key,
            model_label,
            local,
            remote,
            checkpoint,
            result,
        )

    def _detect_field_conflicts(
        self,
        local: SyncRecord,
        remote: SyncRecord,
        checkpoint: int,
    ) -> list[FieldConflict]:
        conflicts: list[FieldConflict] = []

        all_fields = (
            (set(local.data) | set(remote.data)) - META_FIELDS
        )

        for field_name in sorted(all_fields):
            local_timestamp = local.timestamps.get(
                field_name,
                0,
            )

            remote_timestamp = remote.timestamps.get(
                field_name,
                0,
            )

            if local_timestamp <= checkpoint:
                continue

            if remote_timestamp <= checkpoint:
                continue

            local_value = local.data.get(field_name)
            remote_value = remote.data.get(field_name)

            if local_value != remote_value:
                conflicts.append(FieldConflict(
                    field_name=field_name,
                    local_value=local_value,
                    remote_value=remote_value,
                    local_timestamp=local_timestamp,
                    remote_timestamp=remote_timestamp,
                ))

        return conflicts

    def _resolve_conflict(
        self,
        key: str,
        model_label: str,
        local: SyncRecord,
        remote: SyncRecord,
        checkpoint: int,
        result: ReconciliationResult,
    ) -> None:
        field_conflicts = self._detect_field_conflicts(
            local,
            remote,
            checkpoint,
        )

        conflict_type = (
            ConflictType.BOTH_MODIFIED
            if field_conflicts
            else ConflictType.COMPATIBLE
        )

        conflict = RecordConflict(
            key=key,
            model_label=model_label,
            conflict_type=conflict_type,
            field_conflicts=field_conflicts,
            local=local,
            remote=remote,
        )

        try:
            resolution = self._resolver.resolve(conflict)
        except Exception as exception:
            result.errors.append(Error(
                key=key,
                message=f'Conflict resolution failed: {exception}',
                exception=exception,
            ))

            return

        if resolution.record is not None:
            result.to_upsert[key] = resolution.record
            result.response_records[key] = resolution.record

        if conflict_type == ConflictType.BOTH_MODIFIED:
            result.conflict_keys.append(key)

            if field_conflicts:
                result.conflict_log.append(ConflictEntry(
                    conflict=conflict,
                    resolution_source=resolution.source,
                ))
        else:
            result.compatible_keys.append(key)

    def reconcile(
        self,
        payload: ModelPayload,
        local_records: dict[str, SyncRecord],
        checkpoint: int,
    ) -> ReconciliationResult:
        if checkpoint < 0:
            message = (
                f'checkpoint must be non-negative, '
                f'got {checkpoint}'
            )

            raise InvalidParameterError(message)

        result = ReconciliationResult()

        for key, remote in payload.records.items():
            self._classify_record(
                key,
                remote,
                payload.model_label,
                local_records,
                checkpoint,
                result,
            )

        self._classify_deletes(payload, local_records, result)

        return result
