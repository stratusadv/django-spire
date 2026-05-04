from __future__ import annotations

import logging

from contextlib import nullcontext
from dataclasses import dataclass
from typing import Any, Callable, TYPE_CHECKING

from django_spire.contrib.sync.core.enums import SyncStage
from django_spire.contrib.sync.core.hash import RecordHasher
from django_spire.contrib.sync.core.model import Change, Error, Result
from django_spire.contrib.sync.file.exceptions import (
    FileSyncAbortedError,
    FileSyncParameterError
)

if TYPE_CHECKING:
    from contextlib import AbstractContextManager
    from pathlib import Path

    from django_spire.contrib.sync.file.reader.base import Reader
    from django_spire.contrib.sync.file.storage import Storage


logger = logging.getLogger(__name__)


def check_deactivation_threshold(
    threshold: float | None,
    active_count: int,
    deactivation_count: int,
) -> None:
    if threshold is None:
        return

    if not active_count or not deactivation_count:
        return

    ratio = deactivation_count / active_count

    if ratio > threshold:
        message = (
            f'Deactivation ratio {ratio:.1%} exceeds threshold '
            f'{threshold:.1%} '
            f'({deactivation_count} of {active_count} records). '
            f'Set deactivation_threshold=None to disable this check.'
        )
        raise FileSyncAbortedError(message)


def validate_records(
    records: list[dict[str, Any]],
    identity_field: str,
    errors: list[Error],
    progress: Callable[[SyncStage, int, int], None] | None = None,
) -> dict[str, dict[str, Any]]:
    validated: dict[str, dict[str, Any]] = {}
    total = len(records)

    for i, record in enumerate(records):
        raw = record.get(identity_field)

        if raw is None:
            errors.append(Error(
                key='',
                message=f'Record missing identity field: {identity_field}',
            ))

            continue

        key = str(raw).strip()

        if not key:
            errors.append(Error(
                key='',
                message=f'Record has empty identity field: {identity_field}',
            ))

            continue

        if key in validated:
            errors.append(Error(
                key=key,
                message='Duplicate identity value',
            ))

            continue

        validated[key] = record

        if progress:
            progress(SyncStage.VALIDATE, i + 1, total)

    return validated


@dataclass
class _ClassificationResult:
    hashes: dict[str, str]
    new_keys: list[str]
    changed_keys: list[str]
    unchanged_keys: list[str]
    stale_keys: set[str]


class Engine:
    def __init__(
        self,
        storage: Storage,
        identity_field: str,
        compare_fields: list[str] | None = None,
        deactivation_threshold: float | None = 0.5,
        transaction: Callable[[], AbstractContextManager[Any]] | None = None,
        on_created: Callable[[str, dict[str, Any]], None] | None = None,
        on_deactivated: Callable[[str], None] | None = None,
        on_updated: Callable[[str, dict[str, Any], dict[str, Any]], None] | None = None,
        on_complete: Callable[[Result], None] | None = None,
        progress: Callable[[SyncStage, int, int], None] | None = None,
    ) -> None:
        if not identity_field:
            message = 'identity_field must be a non-empty string'
            raise FileSyncParameterError(message)

        if deactivation_threshold is not None and deactivation_threshold < 0.0:
            message = (
                f'deactivation_threshold must be non-negative '
                f'or None, got {deactivation_threshold}'
            )

            raise FileSyncParameterError(message)

        self._identity_field = identity_field
        self._deactivation_threshold = deactivation_threshold
        self._on_complete = on_complete
        self._on_created = on_created
        self._on_deactivated = on_deactivated
        self._on_updated = on_updated
        self._progress = progress
        self._storage = storage
        self._transaction = transaction or nullcontext
        self._hasher = RecordHasher(identity_field, compare_fields)

    def _report_progress(
        self, stage: SyncStage, current: int, total: int,
    ) -> None:
        if self._progress:
            self._progress(stage, current, total)

    def _classify(
        self,
        validated: dict[str, dict[str, Any]],
    ) -> _ClassificationResult:
        incoming_hashes: dict[str, str] = {
            key: self._hasher.hash(record)
            for key, record in validated.items()
        }

        active_keys = self._storage.get_active_keys()
        overlap_keys = validated.keys() & active_keys

        stored_hashes = (
            self._storage.get_hashes(overlap_keys)
            if overlap_keys
            else {}
        )

        new_keys: list[str] = []
        changed_keys: list[str] = []
        unchanged_keys: list[str] = []

        total = len(validated)

        for i, key in enumerate(validated):
            if key not in active_keys:
                new_keys.append(key)
            elif incoming_hashes[key] != stored_hashes.get(key):
                changed_keys.append(key)
            else:
                unchanged_keys.append(key)

            self._report_progress(SyncStage.CLASSIFY, i + 1, total)

        stale_keys = {k for k in active_keys if k not in validated}

        check_deactivation_threshold(
            self._deactivation_threshold,
            len(active_keys),
            len(stale_keys),
        )

        return _ClassificationResult(
            hashes=incoming_hashes,
            new_keys=new_keys,
            changed_keys=changed_keys,
            unchanged_keys=unchanged_keys,
            stale_keys=stale_keys,
        )

    def _mutate(
        self,
        validated: dict[str, dict[str, Any]],
        classified: _ClassificationResult,
    ) -> dict[str, dict[str, Any]]:
        to_create = [validated[k] for k in classified.new_keys]
        to_update = [validated[k] for k in classified.changed_keys]

        create_hashes = {
            k: classified.hashes[k]
            for k in classified.new_keys
        }

        update_hashes = {
            k: classified.hashes[k]
            for k in classified.changed_keys
        }

        with self._transaction():
            old_records: dict[str, dict[str, Any]] = {}

            if classified.changed_keys:
                old_records = self._storage.get_many(
                    set(classified.changed_keys),
                )

            if to_create:
                self._storage.create_many(to_create, create_hashes)

            if to_update:
                self._storage.update_many(to_update, update_hashes)

            if classified.stale_keys:
                self._storage.deactivate_many(classified.stale_keys)

        return old_records

    def _build_changes(
        self,
        validated: dict[str, dict[str, Any]],
        old_records: dict[str, dict[str, Any]],
        changed_keys: list[str],
    ) -> dict[str, Change]:
        return {
            key: Change(old=old_records[key], new=validated[key])
            for key in changed_keys
            if key in old_records
        }

    def _fire_callbacks(
        self,
        validated: dict[str, dict[str, Any]],
        old_records: dict[str, dict[str, Any]],
        result: Result,
    ) -> None:
        if self._on_created:
            for key in result.created:
                try:
                    self._on_created(key, validated[key])
                except Exception as exc:
                    result.errors.append(Error(
                        key=key,
                        message=f'on_created callback failed: {exc}',
                        exception=exc,
                    ))

        if self._on_updated:
            for key in result.updated:
                try:
                    self._on_updated(key, old_records[key], validated[key])
                except Exception as exc:
                    result.errors.append(Error(
                        key=key,
                        message=f'on_updated callback failed: {exc}',
                        exception=exc,
                    ))

        if self._on_deactivated:
            for key in result.deactivated:
                try:
                    self._on_deactivated(key)
                except Exception as exc:
                    result.errors.append(Error(
                        key=key,
                        message=f'on_deactivated callback failed: {exc}',
                        exception=exc,
                    ))

    def _finalize(self, result: Result) -> None:
        if self._on_complete:
            self._on_complete(result)

        for error in result.errors:
            logger.warning('Sync error [%s]: %s', error.key, error.message)

        logger.info(
            'Sync complete: %d created, %d updated, %d deactivated, '
            '%d unchanged, %d errors',
            len(result.created),
            len(result.updated),
            len(result.deactivated),
            len(result.unchanged),
            len(result.errors),
        )

    def sync(
        self,
        file_path: str | Path,
        reader: Reader,
        dry_run: bool = False,
    ) -> Result:
        records = reader.read(file_path)
        return self.sync_records(records, dry_run=dry_run)

    def sync_records(
        self,
        records: list[dict[str, Any]],
        dry_run: bool = False,
    ) -> Result:
        result = Result()

        validated = validate_records(
            records,
            self._identity_field,
            result.errors,
            self._progress,
        )

        classified = self._classify(validated)

        result.created = classified.new_keys
        result.updated = classified.changed_keys
        result.unchanged = classified.unchanged_keys
        result.deactivated = sorted(classified.stale_keys)

        if dry_run:
            return result

        old_records = self._mutate(validated, classified)

        result.changes = self._build_changes(
            validated,
            old_records,
            classified.changed_keys,
        )

        self._fire_callbacks(validated, old_records, result)
        self._finalize(result)

        return result
