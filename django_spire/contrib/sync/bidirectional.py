from __future__ import annotations

import logging

from contextlib import nullcontext
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, TYPE_CHECKING

from django_spire.contrib.sync.conflict import Conflict, ConflictStrategy, Resolution, SourceWins
from django_spire.contrib.sync.enums import ResolutionAction, SyncStage
from django_spire.contrib.sync.hash import RecordHasher
from django_spire.contrib.sync.model import BidirectionalResult, Change, Error

if TYPE_CHECKING:
    from contextlib import AbstractContextManager

    from django_spire.contrib.sync.parser.base import Parser
    from django_spire.contrib.sync.storage import BidirectionalStorage
    from django_spire.contrib.sync.writer.base import Writer


logger = logging.getLogger(__name__)

_TARGET_CREATE = 'target_create'
_TARGET_UPDATE = 'target_update'
_TARGET_DEACTIVATE = 'target_deactivate'
_SOURCE_CREATE = 'source_create'
_SOURCE_UPDATE = 'source_update'
_SOURCE_DEACTIVATE = 'source_deactivate'
_CONFLICT = 'conflict'
_UNCHANGED = 'unchanged'
_BOTH_DELETED = 'both_deleted'


class BidirectionalEngine:
    def __init__(
        self,
        storage: BidirectionalStorage,
        identity_field: str,
        compare_fields: list[str] | None = None,
        conflict_strategy: ConflictStrategy | None = None,
        transaction: Callable[[], AbstractContextManager[Any]] | None = None,
        on_complete: Callable[[BidirectionalResult], None] | None = None,
        progress: Callable[[SyncStage, int, int], None] | None = None,
    ) -> None:
        self._identity_field = identity_field
        self._conflict_strategy = conflict_strategy or SourceWins()
        self._on_complete = on_complete
        self._progress = progress
        self._storage = storage
        self._transaction = transaction or nullcontext
        self._hasher = RecordHasher(identity_field, compare_fields)

    def _report_progress(self, stage: SyncStage, current: int, total: int) -> None:
        if self._progress:
            self._progress(stage, current, total)

    def _validate(
        self,
        records: list[dict[str, Any]],
        result: BidirectionalResult,
    ) -> dict[str, dict[str, Any]]:
        validated: dict[str, dict[str, Any]] = {}
        total = len(records)

        for i, record in enumerate(records):
            raw = record.get(self._identity_field)

            if raw is None:
                result.errors.append(Error(
                    key='',
                    message=f'Record missing identity field: {self._identity_field}',
                ))
                continue

            key = str(raw).strip()

            if not key:
                result.errors.append(Error(
                    key='',
                    message=f'Record has empty identity field: {self._identity_field}',
                ))
                continue

            if key in validated:
                result.errors.append(Error(
                    key=key,
                    message='Duplicate identity value',
                ))
                continue

            validated[key] = record
            self._report_progress(SyncStage.VALIDATE, i + 1, total)

        return validated

    def _classify_mutual(
        self,
        key: str,
        source_hashes: dict[str, str],
        target_hashes: dict[str, str],
        baseline_hashes: dict[str, str],
    ) -> str:
        source_changed = source_hashes[key] != baseline_hashes[key]
        target_changed = target_hashes[key] != baseline_hashes[key]

        if source_changed and target_changed:
            if source_hashes[key] == target_hashes[key]:
                return _UNCHANGED
            return _CONFLICT

        if source_changed:
            return _TARGET_UPDATE

        if target_changed:
            return _SOURCE_UPDATE

        return _UNCHANGED

    def _classify_key(
        self,
        key: str,
        source_hashes: dict[str, str],
        target_hashes: dict[str, str],
        baseline_hashes: dict[str, str],
        in_source: bool,
        in_target: bool,
        in_baseline: bool,
    ) -> str:
        source_changed = (
            in_source and in_baseline
            and source_hashes[key] != baseline_hashes[key]
        )
        target_changed = (
            in_target and in_baseline
            and target_hashes[key] != baseline_hashes[key]
        )

        result = _UNCHANGED

        match (in_source, in_target, in_baseline):
            case (True, True, False):
                if source_hashes[key] != target_hashes[key]:
                    result = _CONFLICT

            case (True, False, False):
                result = _TARGET_CREATE

            case (False, True, False):
                result = _SOURCE_CREATE

            case (False, False, True):
                result = _BOTH_DELETED

            case (False, _, True):
                result = _CONFLICT if target_changed else _TARGET_DEACTIVATE

            case (_, False, True):
                result = _CONFLICT if source_changed else _SOURCE_DEACTIVATE

            case (True, True, True):
                result = self._classify_mutual(
                    key, source_hashes, target_hashes, baseline_hashes,
                )

        return result

    def _classify(
        self,
        source: dict[str, dict[str, Any]],
        target: dict[str, dict[str, Any]],
        baseline_hashes: dict[str, str],
        source_hashes: dict[str, str],
        target_hashes: dict[str, str],
    ) -> tuple[
        list[str],
        list[str],
        set[str],
        list[str],
        list[str],
        set[str],
        list[str],
        list[str],
    ]:
        all_keys = sorted(source.keys() | target.keys() | baseline_hashes.keys())

        target_creates: list[str] = []
        target_updates: list[str] = []
        target_deactivations: set[str] = set()
        source_creates: list[str] = []
        source_updates: list[str] = []
        source_deactivations: set[str] = set()
        conflict_keys: list[str] = []
        unchanged: list[str] = []

        _dispatch = {
            _TARGET_CREATE: target_creates.append,
            _TARGET_UPDATE: target_updates.append,
            _TARGET_DEACTIVATE: target_deactivations.add,
            _SOURCE_CREATE: source_creates.append,
            _SOURCE_UPDATE: source_updates.append,
            _SOURCE_DEACTIVATE: source_deactivations.add,
            _CONFLICT: conflict_keys.append,
            _UNCHANGED: unchanged.append,
        }

        total = len(all_keys)

        for i, key in enumerate(all_keys):
            action = self._classify_key(
                key, source_hashes, target_hashes, baseline_hashes,
                key in source, key in target, key in baseline_hashes,
            )

            handler = _dispatch.get(action)

            if handler:
                handler(key)

            self._report_progress(SyncStage.CLASSIFY, i + 1, total)

        return (
            target_creates,
            target_updates,
            target_deactivations,
            source_creates,
            source_updates,
            source_deactivations,
            conflict_keys,
            unchanged,
        )

    def _resolve_conflicts(
        self,
        conflict_keys: list[str],
        source: dict[str, dict[str, Any]],
        target: dict[str, dict[str, Any]],
        source_timestamp: datetime | None,
        target_timestamps: dict[str, datetime],
        result: BidirectionalResult,
    ) -> dict[str, Resolution]:
        resolved: dict[str, Resolution] = {}

        for key in conflict_keys:
            conflict = Conflict(
                key=key,
                source_record=source.get(key),
                target_record=target.get(key),
                source_timestamp=source_timestamp,
                target_timestamp=target_timestamps.get(key),
            )

            try:
                resolved[key] = self._conflict_strategy.resolve(conflict)
            except Exception as exc:
                result.errors.append(Error(
                    key=key,
                    message=f'Conflict resolution failed: {exc}',
                    exception=exc,
                ))

        return resolved

    def _apply_resolutions(
        self,
        resolved: dict[str, Resolution],
        target_creates: list[str],
        target_updates: list[str],
        target_deactivations: set[str],
        source_creates: list[str],
        source_updates: list[str],
        source_deactivations: set[str],
        source: dict[str, dict[str, Any]],
        target: dict[str, dict[str, Any]],
    ) -> None:
        for key, resolution in resolved.items():
            if resolution.action == ResolutionAction.SKIP:
                continue

            source_record = source.get(key)
            target_record = target.get(key)

            if resolution.action == ResolutionAction.USE_SOURCE:
                if source_record is None:
                    target_deactivations.add(key)
                elif target_record is None:
                    target_creates.append(key)
                else:
                    target_updates.append(key)

            elif resolution.action == ResolutionAction.USE_TARGET:
                if target_record is None:
                    source_deactivations.add(key)
                elif source_record is None:
                    source_creates.append(key)
                else:
                    source_updates.append(key)

    def _mutate_target(
        self,
        source: dict[str, dict[str, Any]],
        source_hashes: dict[str, str],
        target_creates: list[str],
        target_updates: list[str],
        target_deactivations: set[str],
    ) -> dict[str, dict[str, Any]]:
        to_create = [source[k] for k in target_creates if k in source]
        to_update = [source[k] for k in target_updates if k in source]

        create_hashes = {k: source_hashes[k] for k in target_creates if k in source_hashes}
        update_hashes = {k: source_hashes[k] for k in target_updates if k in source_hashes}

        old_records: dict[str, dict[str, Any]] = {}

        with self._transaction():
            if target_updates:
                old_records = self._storage.get_many(set(target_updates))

            if to_create:
                self._storage.create_many(to_create, create_hashes)

            if to_update:
                self._storage.update_many(to_update, update_hashes)

            if target_deactivations:
                self._storage.deactivate_many(target_deactivations)

        return old_records

    def _mutate_source(
        self,
        source: dict[str, dict[str, Any]],
        target: dict[str, dict[str, Any]],
        source_creates: list[str],
        source_updates: list[str],
        source_deactivations: set[str],
        resolved: dict[str, Resolution],
        file_path: Path,
        writer: Writer,
    ) -> None:
        has_source_changes = (
            source_creates
            or source_updates
            or source_deactivations
            or any(
                r.action == ResolutionAction.USE_TARGET
                for r in resolved.values()
            )
        )

        if not has_source_changes:
            return

        final_records = dict(source)

        for key in source_creates:
            if key in target:
                final_records[key] = target[key]

        for key in source_updates:
            if key in target:
                final_records[key] = target[key]

        for key, resolution in resolved.items():
            if resolution.action == ResolutionAction.USE_TARGET:
                if resolution.record is not None:
                    final_records[key] = resolution.record
                else:
                    final_records.pop(key, None)

        for key in source_deactivations:
            final_records.pop(key, None)

        writer.write(file_path, list(final_records.values()))

    def _compute_baseline(
        self,
        source_hashes: dict[str, str],
        target_hashes: dict[str, str],
        baseline_hashes: dict[str, str],
        target_creates: list[str],
        target_updates: list[str],
        target_deactivations: set[str],
        source_creates: list[str],
        source_updates: list[str],
        source_deactivations: set[str],
        resolved: dict[str, Resolution],
    ) -> dict[str, str]:
        new_baseline: dict[str, str] = {}

        all_active = (
            (set(source_hashes) | set(target_hashes))
            - target_deactivations
            - source_deactivations
        )

        target_from_source = set(target_creates) | set(target_updates)
        source_from_target = set(source_creates) | set(source_updates)

        for key in all_active:
            if key in resolved:
                res = resolved[key]

                if res.action == ResolutionAction.USE_SOURCE and key in source_hashes:
                    new_baseline[key] = source_hashes[key]
                elif res.action == ResolutionAction.USE_TARGET and key in target_hashes:
                    new_baseline[key] = target_hashes[key]
                elif res.action == ResolutionAction.SKIP and key in baseline_hashes:
                    new_baseline[key] = baseline_hashes[key]
            elif key in target_from_source and key in source_hashes:
                new_baseline[key] = source_hashes[key]
            elif key in source_from_target and key in target_hashes:
                new_baseline[key] = target_hashes[key]
            elif key in source_hashes:
                new_baseline[key] = source_hashes[key]
            elif key in target_hashes:
                new_baseline[key] = target_hashes[key]

        return new_baseline

    def _get_file_timestamp(self, file_path: Path) -> datetime | None:
        try:
            mtime = file_path.stat().st_mtime
            return datetime.fromtimestamp(mtime, tz=UTC)
        except OSError:
            return None

    def sync(
        self,
        file_path: str | Path,
        parser: Parser,
        writer: Writer,
        dry_run: bool = False,
    ) -> BidirectionalResult:
        file_path = Path(file_path)
        result = BidirectionalResult()

        raw_records = parser.parse(file_path)
        source = self._validate(raw_records, result)

        active_keys = self._storage.get_active_keys()
        target = self._storage.get_many(active_keys) if active_keys else {}

        source_hashes = {k: self._hasher.hash(v) for k, v in source.items()}
        target_hashes = {k: self._hasher.hash(v) for k, v in target.items()}
        baseline_hashes = self._storage.get_baseline_hashes()

        (
            target_creates,
            target_updates,
            target_deactivations,
            source_creates,
            source_updates,
            source_deactivations,
            conflict_keys,
            unchanged,
        ) = self._classify(source, target, baseline_hashes, source_hashes, target_hashes)

        source_timestamp = self._get_file_timestamp(file_path)
        target_timestamps = (
            self._storage.get_timestamps(set(conflict_keys))
            if conflict_keys
            else {}
        )

        resolved = self._resolve_conflicts(
            conflict_keys, source, target,
            source_timestamp, target_timestamps, result,
        )

        self._apply_resolutions(
            resolved,
            target_creates, target_updates, target_deactivations,
            source_creates, source_updates, source_deactivations,
            source, target,
        )

        result.target_created = target_creates
        result.target_updated = target_updates
        result.target_deactivated = sorted(target_deactivations)
        result.source_created = source_creates
        result.source_updated = source_updates
        result.source_deactivated = sorted(source_deactivations)
        result.conflicts = resolved
        result.unchanged = unchanged

        if dry_run:
            return result

        old_records = self._mutate_target(
            source, source_hashes,
            target_creates, target_updates, target_deactivations,
        )

        self._mutate_source(
            source, target,
            source_creates, source_updates, source_deactivations,
            resolved, file_path, writer,
        )

        new_baseline = self._compute_baseline(
            source_hashes, target_hashes, baseline_hashes,
            target_creates, target_updates, target_deactivations,
            source_creates, source_updates, source_deactivations,
            resolved,
        )

        self._storage.save_baseline_hashes(new_baseline)

        for key in target_updates:
            if key in old_records and key in source:
                result.changes[key] = Change(old=old_records[key], new=source[key])

        for key in source_updates:
            if key in target and key in source:
                result.changes[key] = Change(old=source[key], new=target[key])

        if self._on_complete:
            self._on_complete(result)

        for error in result.errors:
            logger.warning('Sync error [%s]: %s', error.key, error.message)

        logger.info(
            'Bidirectional sync complete: '
            'target(%d created, %d updated, %d deactivated) '
            'source(%d created, %d updated, %d deactivated) '
            '%d conflicts, %d unchanged, %d errors',
            len(result.target_created),
            len(result.target_updated),
            len(result.target_deactivated),
            len(result.source_created),
            len(result.source_updated),
            len(result.source_deactivated),
            len(result.conflicts),
            len(result.unchanged),
            len(result.errors),
        )

        return result
