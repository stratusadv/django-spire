from __future__ import annotations

import json
import logging
import time

from contextlib import contextmanager, nullcontext
from typing import Any, Iterator, TYPE_CHECKING

from django_spire.contrib.sync.core.enums import (
    SyncPhase,
    SyncStage,
    SyncStatus,
)
from django_spire.contrib.sync.core.exceptions import (
    ClockDriftError,
    InvalidParameterError,
    ManifestChecksumError,
    PayloadLimitError,
    SyncAbortedError,
    TransportRequiredError,
)
from django_spire.contrib.sync.core.model import Error
from django_spire.contrib.sync.database.manifest import (
    DatabaseResult,
    ModelPayload,
    SyncManifest,
)
from django_spire.contrib.sync.database.reconciler import (
    PayloadReconciler,
    ReconciliationResult,
)
from django_spire.contrib.sync.database.record import SyncRecord

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractContextManager

    from django_spire.contrib.sync.core.clock import HybridLogicalClock
    from django_spire.contrib.sync.core.graph import DependencyGraph
    from django_spire.contrib.sync.database.lock import SyncLock
    from django_spire.contrib.sync.database.storage import (
        DatabaseSyncStorage,
    )
    from django_spire.contrib.sync.database.transport.base import (
        Transport,
    )


logger = logging.getLogger(__name__)

BATCH_BYTES_DEFAULT = 16 * 1024 * 1024
CLOCK_DRIFT_MAX_DEFAULT = 300


class _Budget:
    def __init__(
        self,
        records_max: int | None = None,
        bytes_max: int | None = None,
    ) -> None:
        self._records_max = records_max
        self._bytes_max = bytes_max
        self._records = 0
        self._bytes = 0

    @property
    def consumed_bytes(self) -> int:
        return self._bytes

    @property
    def consumed_records(self) -> int:
        return self._records

    @property
    def exhausted(self) -> bool:
        if self._records_max is not None:
            if self._records >= self._records_max:
                return True

        if self._bytes_max is not None:
            if self._bytes >= self._bytes_max:
                return True

        return False

    @property
    def remaining_records(self) -> int | None:
        if self._records_max is None:
            return None

        return max(0, self._records_max - self._records)

    def can_fit(self, records: int, bytes_: int) -> bool:
        if self._records_max is not None:
            if self._records + records > self._records_max:
                return False

        if self._bytes_max is not None and self._records > 0:
            if self._bytes + bytes_ > self._bytes_max:
                return False

        return True

    def consume(self, records: int, bytes_: int) -> None:
        self._records += records
        self._bytes += bytes_


def _record_size(record: SyncRecord) -> int:
    return len(json.dumps(record.to_dict(), ensure_ascii=True))


def _last_cursor(
    records: dict[str, SyncRecord],
) -> dict[str, Any] | None:
    if not records:
        return None

    last_key = list(records.keys())[-1]
    last_record = records[last_key]

    return {
        'key': last_key,
        'timestamp': last_record.sync_field_last_modified,
    }


class DatabaseEngine:
    def __init__(
        self,
        storage: DatabaseSyncStorage,
        graph: DependencyGraph,
        clock: HybridLogicalClock,
        node_id: str,
        *,
        batch_bytes: int | None = BATCH_BYTES_DEFAULT,
        batch_size: int | None = None,
        clock_drift_max: int | None = CLOCK_DRIFT_MAX_DEFAULT,
        identity_field: str = 'id',
        lock: SyncLock | None = None,
        on_complete: Callable[[DatabaseResult], None] | None = None,
        on_phase: Callable[[SyncPhase], None] | None = None,
        payload_bytes_max: int | None = None,
        payload_records_max: int | None = None,
        progress: Callable[[SyncStage, int, int], None] | None = None,
        reconciler: PayloadReconciler | None = None,
        transaction: Callable[[], AbstractContextManager[Any]] = nullcontext,
        transport: Transport | None = None,
    ) -> None:
        if not node_id:
            message = 'node_id must be a non-empty string'
            raise InvalidParameterError(message)

        if not identity_field:
            message = 'identity_field must be a non-empty string'
            raise InvalidParameterError(message)

        if batch_bytes is not None and batch_bytes < 1:
            message = (
                f'batch_bytes must be >= 1 '
                f'or None, got {batch_bytes}'
            )

            raise InvalidParameterError(message)

        if batch_size is not None and batch_size < 1:
            message = (
                f'batch_size must be >= 1 '
                f'or None, got {batch_size}'
            )

            raise InvalidParameterError(message)

        if clock_drift_max is not None and clock_drift_max < 0:
            message = (
                f'clock_drift_max must be non-negative '
                f'or None, got {clock_drift_max}'
            )

            raise InvalidParameterError(message)

        if payload_bytes_max is not None and payload_bytes_max < 1:
            message = (
                f'payload_bytes_max must be >= 1 '
                f'or None, got {payload_bytes_max}'
            )

            raise InvalidParameterError(message)

        if payload_records_max is not None and payload_records_max < 1:
            message = (
                f'payload_records_max must be >= 1 '
                f'or None, got {payload_records_max}'
            )

            raise InvalidParameterError(message)

        self._batch_bytes = batch_bytes
        self._batch_size = batch_size
        self._clock = clock
        self._clock_drift_max = clock_drift_max
        self._graph = graph
        self._identity_field = identity_field
        self._lock = lock
        self._node_id = node_id
        self._on_complete = on_complete
        self._on_phase = on_phase
        self._payload_bytes_max = payload_bytes_max
        self._payload_records_max = payload_records_max
        self._progress = progress
        self._reconciler = reconciler or PayloadReconciler()
        self._storage = storage
        self._transaction = transaction
        self._transport = transport

    def _advance_clock(self, manifest: SyncManifest) -> None:
        wall = max(
            self._max_applied_timestamp(manifest),
            manifest.checkpoint,
        )

        if wall:
            self._clock.receive(wall)

    def _apply_incoming(
        self,
        payloads: list[ModelPayload],
        checkpoint: int,
        result: DatabaseResult,
        received_at: int = 0,
        records_max: int | None = None,
        bytes_max: int | None = None,
        after_keys: dict[str, Any] | None = None,
    ) -> tuple[list[ModelPayload], bool, dict[str, Any]]:
        incoming_by_label = {
            payload.model_label: payload
            for payload in payloads
        }

        resolved_after_keys = after_keys or {}
        response_payloads: list[ModelPayload] = []
        response_cursors: dict[str, Any] = {}
        budget = _Budget(records_max, bytes_max)
        has_more = False

        for model_label in self._graph.sync_order():
            incoming_payload = incoming_by_label.get(model_label)

            if incoming_payload is not None:
                response_payload, truncated = self._process_model(
                    incoming_payload,
                    checkpoint,
                    result,
                    received_at=received_at,
                    budget=budget,
                )

                if truncated:
                    has_more = True

                    if response_payload.records:
                        payload_cursor = _last_cursor(
                            response_payload.records,
                        )

                        if payload_cursor:
                            response_cursors[model_label] = payload_cursor

                if response_payload.records or response_payload.deletes:
                    response_payloads.append(response_payload)

                continue

            if budget.exhausted:
                probe = self._storage.get_changed_since(
                    model_label, checkpoint, limit=1,
                )

                if probe:
                    has_more = True

                continue

            cursor = resolved_after_keys.get(model_label)

            local_payload, truncated = self._collect_local_only_payload(
                model_label,
                checkpoint,
                budget,
                cursor=cursor,
            )

            if truncated:
                has_more = True

                if local_payload is not None:
                    payload_cursor = _last_cursor(local_payload.records)

                    if payload_cursor:
                        response_cursors[model_label] = payload_cursor

            if local_payload is not None:
                response_payloads.append(local_payload)

        return response_payloads, has_more, response_cursors

    def _apply_reconciliation(
        self,
        model_label: str,
        reconciliation: ReconciliationResult,
        result: DatabaseResult,
        received_at: int = 0,
    ) -> None:
        skipped: set[str] = set()

        if reconciliation.to_upsert:
            records = reconciliation.to_upsert

            if received_at:
                records = {
                    key: SyncRecord(
                        key=record.key,
                        data=record.data,
                        timestamps=record.timestamps,
                        received_at=received_at,
                    )
                    for key, record in records.items()
                }

            skipped = self._storage.upsert_many(
                model_label,
                records,
            )

        if reconciliation.to_delete:
            self._storage.delete_many(
                model_label,
                reconciliation.to_delete,
            )

        self._merge_into_result(
            model_label,
            reconciliation,
            skipped,
            result,
        )

    def _apply_response(
        self,
        response: SyncManifest,
        result: DatabaseResult,
    ) -> None:
        known = self._graph.known_models()
        ordered = self._order_payloads(response.payloads)

        for payload in ordered:
            if payload.model_label not in known:
                logger.warning(
                    'Ignoring unknown model %r in response',
                    payload.model_label,
                )

                continue

            if payload.records:
                self._apply_response_records(payload, result)

            if payload.deletes:
                self._apply_response_deletes(payload, result)

    def _apply_response_deletes(
        self,
        payload: ModelPayload,
        result: DatabaseResult,
    ) -> None:
        existing = self._storage.get_records(
            payload.model_label,
            set(payload.deletes.keys()),
        )

        to_delete: dict[str, int] = {}

        for key, tombstone_ts in payload.deletes.items():
            local = existing.get(key)

            if local is None:
                to_delete[key] = tombstone_ts
            elif local.sync_field_last_modified <= tombstone_ts:
                to_delete[key] = tombstone_ts
            else:
                logger.info(
                    'Skipping delete for %s:%s: '
                    'local modified after tombstone',
                    payload.model_label,
                    key,
                )

                result.skipped[payload.model_label].append(key)

        if to_delete:
            self._storage.delete_many(
                payload.model_label,
                to_delete,
            )

            for key in to_delete:
                result.deleted[payload.model_label].append(key)

    def _apply_response_records(
        self,
        payload: ModelPayload,
        result: DatabaseResult,
    ) -> None:
        skipped = self._storage.upsert_many(
            payload.model_label,
            payload.records,
        )

        applied_keys = set(payload.records.keys()) - skipped
        result.applied[payload.model_label].extend(applied_keys)

        for key in skipped:
            result.skipped[payload.model_label].append(key)

    def _check_clock_drift(self, remote_time: int) -> int:
        local_time = int(time.time())
        drift = abs(local_time - remote_time)

        if self._clock_drift_max is not None:
            if drift > self._clock_drift_max:
                message = (
                    f'Clock drift of {drift}s exceeds '
                    f'threshold of {self._clock_drift_max}s. '
                    f'Local time: {local_time}, '
                    f'remote time: {remote_time}. '
                    f'Ensure NTP is enabled on both nodes, '
                    f'or set clock_drift_max=None to disable.'
                )

                raise ClockDriftError(message)

        if drift > 0:
            logger.debug('Clock drift: %ds', drift)

        return drift

    def _collect(
        self,
        checkpoint: int,
        limit: int | None = None,
        bytes_limit: int | None = None,
        after_keys: dict[str, Any] | None = None,
    ) -> SyncManifest:
        resolved_after_keys = after_keys or {}
        budget = _Budget(limit, bytes_limit)
        payloads: list[ModelPayload] = []
        cursors: dict[str, Any] = {}
        has_more = False

        for model_label in self._graph.sync_order():
            if budget.exhausted:
                probe = self._storage.get_changed_since(
                    model_label,
                    checkpoint,
                    limit=1,
                )

                if probe:
                    has_more = True

                continue

            cursor = resolved_after_keys.get(model_label)

            record_limit = budget.remaining_records

            fetch_limit = (
                None if record_limit is None
                else record_limit + 1
            )

            effective_ts = checkpoint
            effective_after_key = None

            if cursor:
                effective_ts = cursor.get('timestamp', checkpoint)
                effective_after_key = cursor.get('key')

            records = self._storage.get_changed_since(
                model_label,
                effective_ts,
                limit=fetch_limit,
                after_key=effective_after_key,
            )

            if (
                record_limit is not None
                and len(records) > record_limit
            ):
                records = dict(list(records.items())[:record_limit])
                has_more = True

            accepted: dict[str, SyncRecord] = {}

            for key, record in records.items():
                record_bytes = _record_size(record)

                if not budget.can_fit(1, record_bytes):
                    has_more = True
                    break

                accepted[key] = record
                budget.consume(1, record_bytes)

            if has_more and accepted:
                payload_cursor = _last_cursor(accepted)

                if payload_cursor:
                    cursors[model_label] = payload_cursor

            deletes = self._storage.get_deletes_since(
                model_label,
                checkpoint,
            )

            if accepted or deletes:
                payloads.append(ModelPayload(
                    model_label=model_label,
                    records=accepted,
                    deletes=deletes,
                ))

        if self._payload_records_max is not None:
            if budget.consumed_records > self._payload_records_max:
                message = (
                    f'Collected {budget.consumed_records} records '
                    f'exceeds payload_records_max='
                    f'{self._payload_records_max}. '
                    f'Sync more frequently or increase '
                    f'the limit.'
                )

                raise PayloadLimitError(message)

        if self._payload_bytes_max is not None:
            if budget.consumed_bytes > self._payload_bytes_max:
                message = (
                    f'Collected {budget.consumed_bytes} bytes '
                    f'exceeds payload_bytes_max='
                    f'{self._payload_bytes_max}. '
                    f'Sync more frequently or increase '
                    f'the limit.'
                )

                raise PayloadLimitError(message)

        manifest = SyncManifest(
            node_id=self._node_id,
            checkpoint=checkpoint,
            node_time=int(time.time()),
            payloads=payloads,
            has_more=has_more,
        )

        manifest.after_keys = cursors

        return manifest

    def _collect_local_only_payload(
        self,
        model_label: str,
        checkpoint: int,
        budget: _Budget,
        cursor: dict[str, Any] | None = None,
    ) -> tuple[ModelPayload | None, bool]:
        record_limit = budget.remaining_records

        fetch_limit = (
            None if record_limit is None
            else record_limit + 1
        )

        effective_ts = checkpoint
        effective_after_key = None

        if cursor:
            effective_ts = cursor.get('timestamp', checkpoint)
            effective_after_key = cursor.get('key')

        records = self._storage.get_changed_since(
            model_label,
            effective_ts,
            limit=fetch_limit,
            after_key=effective_after_key,
        )

        truncated = False

        if (
            record_limit is not None
            and len(records) > record_limit
        ):
            records = dict(
                list(records.items())[:record_limit]
            )

            truncated = True

        accepted: dict[str, SyncRecord] = {}

        for key, record in records.items():
            record_bytes = _record_size(record)

            if not budget.can_fit(1, record_bytes):
                truncated = True
                break

            accepted[key] = record
            budget.consume(1, record_bytes)

        deletes = self._storage.get_deletes_since(
            model_label, checkpoint,
        )

        if not accepted and not deletes:
            return None, truncated

        return ModelPayload(
            model_label=model_label,
            records=accepted,
            deletes=deletes,
        ), truncated

    def _commit(
        self,
        checkpoint: int,
        response: SyncManifest,
        sent_snapshot: dict[str, dict[str, int]],
        received_snapshot: dict[str, dict[str, int]],
        result: DatabaseResult,
        server_cursors: dict[str, Any] | None = None,
        collect_cursors: dict[str, Any] | None = None,
    ) -> None:
        with self._transaction():
            self._apply_response(response, result)

            target_checkpoint = max(response.checkpoint, checkpoint)

            safe_checkpoint = self._compute_safe_checkpoint(
                checkpoint,
                target_checkpoint,
                sent_snapshot,
                received_snapshot,
            )

            persisted_cursors = {}

            if server_cursors:
                persisted_cursors.update({
                    f'server:{k}': v
                    for k, v in server_cursors.items()
                })

            if collect_cursors:
                persisted_cursors.update({
                    f'collect:{k}': v
                    for k, v in collect_cursors.items()
                })

            self._storage.save_checkpoint(
                self._node_id,
                safe_checkpoint,
                after_keys=persisted_cursors or None,
            )

    def _compute_safe_checkpoint(
        self,
        old_checkpoint: int,
        new_checkpoint: int,
        sent_snapshot: dict[str, dict[str, int]],
        received_snapshot: dict[str, dict[str, int]],
    ) -> int:
        if new_checkpoint < old_checkpoint:
            message = (
                f'New checkpoint {new_checkpoint} precedes '
                f'old checkpoint {old_checkpoint}'
            )

            raise SyncAbortedError(message)

        unsent_min = new_checkpoint

        for model_label in self._graph.sync_order():
            changes = self._storage.get_changed_since(
                model_label,
                old_checkpoint,
            )

            sent_lms = sent_snapshot.get(model_label, {})

            received_lms = received_snapshot.get(
                model_label,
                {},
            )

            for key, record in changes.items():
                sent_lm = sent_lms.get(key)
                received_lm = received_lms.get(key)
                lm = record.sync_field_last_modified

                if sent_lm is not None:
                    if lm == sent_lm:
                        continue

                if received_lm is not None:
                    if lm == received_lm:
                        continue

                unsent_min = min(unsent_min, lm)

        if unsent_min < new_checkpoint:
            return max(unsent_min - 1, old_checkpoint)

        return new_checkpoint

    def _enter_phase(
        self,
        phase: SyncPhase,
        session_id: str,
        stage: SyncStage | None = None,
    ) -> None:
        self._report_phase(phase, session_id)

        if stage is not None:
            self._report_progress(stage, 0, 1)

    def _exchange_and_validate(
        self,
        manifest: SyncManifest,
    ) -> SyncManifest:
        response = self._transport.exchange(manifest)
        self._validate_manifest(response)
        self._validate_clock(response)

        return response

    def _extract_record_snapshot(
        self,
        manifest: SyncManifest,
    ) -> dict[str, dict[str, int]]:
        return {
            payload.model_label: {
                key: record.sync_field_last_modified
                for key, record in payload.records.items()
            }
            for payload in manifest.payloads
        }

    def _finalize(self, result: DatabaseResult) -> None:
        if self._on_complete:
            self._on_complete(result)

        for error in result.errors:
            logger.warning(
                'Sync error [%s]: %s',
                error.key,
                error.message,
            )

    def _get_local_only_changes(
        self,
        model_label: str,
        checkpoint: int,
        incoming_keys: set[str],
        limit: int | None = None,
    ) -> tuple[dict[str, SyncRecord], bool]:
        fetch_limit = (
            None if limit is None
            else limit + len(incoming_keys) + 1
        )

        all_changes = self._storage.get_changed_since(
            model_label,
            checkpoint,
            limit=fetch_limit,
        )

        result = {
            key: record
            for key, record in all_changes.items()
            if key not in incoming_keys
        }

        truncated = False

        if limit is not None and len(result) > limit:
            result = dict(list(result.items())[:limit])

            truncated = True

        return result, truncated

    def _log_sync_summary(
        self, result: DatabaseResult,
    ) -> None:
        logger.info(
            'Database sync complete: '
            '%d models pushed, %d models applied, '
            '%d models with conflicts, %d errors',
            len(result.pushed),
            len(result.applied),
            len(result.conflicts),
            len(result.errors),
        )

    @contextmanager
    def _managed_session(
        self,
        result: DatabaseResult | None = None,
    ) -> Iterator[str]:
        session_id = ''

        if self._lock:
            session_id = self._lock.acquire(self._node_id)

        status = SyncStatus.ERROR

        try:
            yield session_id
            status = SyncStatus.SUCCESS
        except SyncAbortedError:
            status = SyncStatus.FAILURE
            raise
        finally:
            if self._lock and session_id:
                try:
                    self._lock.release(
                        session_id,
                        status,
                        result=result,
                    )
                except Exception:
                    logger.exception(
                        'Failed to release sync lock '
                        'for node %s',
                        self._node_id,
                    )

    def _max_applied_timestamp(
        self, manifest: SyncManifest,
    ) -> int:
        timestamp_max = 0

        for payload in manifest.payloads:
            for record in payload.records.values():
                timestamp_max = max(
                    timestamp_max,
                    record.sync_field_last_modified,
                )

            for tombstone_ts in payload.deletes.values():
                timestamp_max = max(
                    timestamp_max,
                    tombstone_ts,
                )

        return timestamp_max

    @staticmethod
    def _max_response_checkpoint(
        incoming_checkpoint: int,
        response_payloads: list[ModelPayload],
    ) -> int:
        result = incoming_checkpoint

        for payload in response_payloads:
            for record in payload.records.values():
                lm = record.sync_field_last_modified

                if lm > result:
                    result = lm

            for tombstone_ts in payload.deletes.values():
                if tombstone_ts > result:
                    result = tombstone_ts

        return result

    def _merge_into_result(
        self,
        model_label: str,
        reconciliation: ReconciliationResult,
        skipped: set[str],
        result: DatabaseResult,
    ) -> None:
        for key in reconciliation.created_keys:
            if key not in skipped:
                result.created[model_label].append(key)

        for key in reconciliation.applied_keys:
            if key not in skipped:
                result.applied[model_label].append(key)

        for key in reconciliation.conflict_keys:
            if key not in skipped:
                result.conflicts[model_label].append(key)

        for key in reconciliation.compatible_keys:
            if key not in skipped:
                result.compatible[model_label].append(key)

        for key in reconciliation.to_delete:
            result.deleted[model_label].append(key)

        for key in skipped:
            result.skipped[model_label].append(key)

        result.errors.extend(reconciliation.errors)
        result.conflict_log.extend(reconciliation.conflict_log)

    def _order_payloads(
        self,
        payloads: list[ModelPayload],
    ) -> list[ModelPayload]:
        order = self._graph.sync_order()

        position = {
            label: index
            for index, label in enumerate(order)
        }

        return sorted(
            payloads,
            key=lambda p: position.get(
                p.model_label,
                len(position),
            ),
        )

    def _process_model(
        self,
        payload: ModelPayload,
        checkpoint: int,
        result: DatabaseResult,
        received_at: int = 0,
        budget: _Budget | None = None,
    ) -> tuple[ModelPayload, bool]:
        all_incoming_keys = (
            set(payload.records) |
            set(payload.deletes)
        )

        local_records = self._storage.get_records(
            payload.model_label,
            all_incoming_keys,
        )

        reconciliation = self._reconciler.reconcile(
            payload,
            local_records,
            checkpoint,
        )

        self._apply_reconciliation(
            payload.model_label, reconciliation, result,
            received_at=received_at,
        )

        response_records: dict[str, SyncRecord] = {}
        truncated = False

        for key, record in reconciliation.response_records.items():
            if received_at:
                record = SyncRecord(
                    key=record.key,
                    data=record.data,
                    timestamps=record.timestamps,
                    received_at=received_at,
                )

            response_records[key] = record

        local_only_limit = (
            None if budget is None
            else budget.remaining_records
        )

        local_only, local_truncated = self._get_local_only_changes(
            payload.model_label,
            checkpoint,
            all_incoming_keys,
            limit=local_only_limit,
        )

        if local_truncated:
            truncated = True

        for key, record in local_only.items():
            if key in response_records:
                continue

            record_bytes = _record_size(record)

            if budget is not None and not budget.can_fit(1, record_bytes):
                truncated = True
                break

            response_records[key] = record

            if budget is not None:
                budget.consume(1, record_bytes)

        local_deletes = self._storage.get_deletes_since(
            payload.model_label, checkpoint,
        )

        for key in all_incoming_keys:
            local_deletes.pop(key, None)

        for key in response_records:
            local_deletes.pop(key, None)

        return ModelPayload(
            model_label=payload.model_label,
            records=response_records,
            deletes=local_deletes,
        ), truncated

    def _record_pushed(
        self,
        manifest: SyncManifest,
        result: DatabaseResult,
    ) -> None:
        for payload in manifest.payloads:
            keys = list(payload.records.keys())

            if keys:
                result.pushed[payload.model_label].extend(keys)

    def _report_phase(
        self,
        phase: SyncPhase,
        session_id: str = '',
    ) -> None:
        if self._lock and session_id:
            self._lock.update_phase(session_id, phase)

        if self._on_phase:
            self._on_phase(phase)

    def _report_progress(
        self,
        stage: SyncStage,
        current: int,
        total: int,
    ) -> None:
        if self._progress:
            self._progress(stage, current, total)

    def _validate_clock(
        self, manifest: SyncManifest,
    ) -> None:
        if manifest.node_time:
            self._check_clock_drift(manifest.node_time)

        self._advance_clock(manifest)

    def _validate_incoming_models(
        self,
        incoming: SyncManifest,
        result: DatabaseResult,
    ) -> list[ModelPayload]:
        known = self._graph.known_models()
        valid: list[ModelPayload] = []

        for payload in incoming.payloads:
            if payload.model_label not in known:
                logger.warning(
                    'Ignoring unknown model '
                    '%r from node %s',
                    payload.model_label,
                    incoming.node_id,
                )

                for key in (
                    set(payload.records) |
                    set(payload.deletes)
                ):
                    result.errors.append(Error(
                        key=key,
                        message=(
                            f'Unknown model: '
                            f'{payload.model_label!r}'
                        ),
                    ))

                continue

            valid.append(payload)

        return valid

    def _validate_manifest(
        self, manifest: SyncManifest,
    ) -> None:
        if not manifest.checksum:
            message = 'Manifest is missing a checksum'
            raise ManifestChecksumError(message)

        if manifest.checksum != manifest.compute_checksum():
            message = 'Manifest checksum verification failed'
            raise ManifestChecksumError(message)

    def process(
        self,
        incoming: SyncManifest,
    ) -> tuple[SyncManifest, DatabaseResult]:
        result = DatabaseResult()

        self._validate_manifest(incoming)
        self._validate_clock(incoming)

        valid_payloads = self._validate_incoming_models(
            incoming, result,
        )

        with self._transaction():
            if self._lock:
                self._lock.hold(self._node_id)

            now = self._clock.now()

            response_payloads, has_more, after_keys = self._apply_incoming(
                valid_payloads,
                incoming.checkpoint,
                result,
                received_at=now,
                records_max=self._batch_size,
                bytes_max=self._batch_bytes,
                after_keys=incoming.after_keys,
            )

        checkpoint_value = self._max_response_checkpoint(
            incoming.checkpoint,
            response_payloads,
        )

        has_activity = (
            any(p.records or p.deletes for p in valid_payloads)
            or any(p.records or p.deletes for p in response_payloads)
        )

        if not has_more and not has_activity:
            checkpoint_value = max(checkpoint_value, now)

        response = SyncManifest(
            node_id=self._node_id,
            checkpoint=checkpoint_value,
            after_keys=after_keys,
            node_time=int(time.time()),
            payloads=response_payloads,
            has_more=has_more,
        )

        response.checksum = response.compute_checksum()

        self._finalize(result)

        return response, result

    def sync(self, dry_run: bool = False) -> DatabaseResult:
        if self._transport is None:
            message = (
                'Transport is required for sync(). '
                'Use process() for server-side.'
            )

            raise TransportRequiredError(message)

        result = DatabaseResult()

        persisted = self._storage.get_after_keys(self._node_id)

        server_cursors: dict[str, Any] = {
            k.removeprefix('server:'): v
            for k, v in persisted.items()
            if k.startswith('server:')
        }

        collect_cursors: dict[str, Any] = {
            k.removeprefix('collect:'): v
            for k, v in persisted.items()
            if k.startswith('collect:')
        }

        with self._managed_session(result) as session_id:
            while True:
                self._enter_phase(
                    SyncPhase.COLLECTING,
                    session_id,
                    SyncStage.VALIDATE,
                )

                checkpoint = self._storage.get_checkpoint(
                    self._node_id,
                )

                manifest = self._collect(
                    checkpoint,
                    limit=self._batch_size,
                    bytes_limit=self._batch_bytes,
                    after_keys=collect_cursors,
                )

                manifest.after_keys = server_cursors
                manifest.checksum = manifest.compute_checksum()

                sent_snapshot = self._extract_record_snapshot(
                    manifest,
                )

                self._record_pushed(manifest, result)

                self._enter_phase(
                    SyncPhase.EXCHANGING, session_id,
                    SyncStage.CLASSIFY,
                )

                response = self._exchange_and_validate(manifest)

                received_snapshot = self._extract_record_snapshot(
                    response,
                )

                self._enter_phase(
                    SyncPhase.RECONCILING, session_id,
                    SyncStage.MUTATE,
                )

                if manifest.has_more:
                    collect_cursors = {}

                    for payload in manifest.payloads:
                        cursor = _last_cursor(payload.records)

                        if cursor:
                            collect_cursors[payload.model_label] = cursor
                else:
                    collect_cursors = {}

                if response.has_more:
                    server_cursors = response.after_keys
                else:
                    server_cursors = {}

                if not dry_run:
                    self._enter_phase(
                        SyncPhase.COMMITTING,
                        session_id,
                    )

                    self._commit(
                        checkpoint, response,
                        sent_snapshot, received_snapshot,
                        result,
                        server_cursors=server_cursors,
                        collect_cursors=collect_cursors,
                    )

                converged = (
                    not manifest.has_more
                    and not response.has_more
                )

                if dry_run:
                    break

                if converged:
                    exchanged = (
                        any(p.records or p.deletes for p in manifest.payloads)
                        or any(p.records or p.deletes for p in response.payloads)
                    )

                    if not exchanged:
                        break

            self._enter_phase(SyncPhase.COMPLETE, session_id)
            self._finalize(result)

        self._log_sync_summary(result)

        return result
