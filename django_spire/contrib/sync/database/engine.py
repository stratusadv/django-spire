from __future__ import annotations

import logging
import time

from collections import defaultdict
from contextlib import AbstractContextManager, contextmanager, nullcontext
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
from django_spire.contrib.sync.database.reconciler import PayloadReconciler
from django_spire.contrib.sync.database.storage import UpsertResult

if TYPE_CHECKING:
    from collections.abc import Callable

    from django_spire.contrib.sync.core.clock import HybridLogicalClock
    from django_spire.contrib.sync.database.graph import DependencyGraph
    from django_spire.contrib.sync.database.lock import SyncLock
    from django_spire.contrib.sync.database.reconciler import (
        ReconciliationResult,
    )
    from django_spire.contrib.sync.database.record import SyncRecord
    from django_spire.contrib.sync.database.storage import DatabaseSyncStorage
    from django_spire.contrib.sync.database.transport import Transport


logger = logging.getLogger(__name__)


BATCH_BYTES_DEFAULT = 2 * 1024 * 1024
CLOCK_DRIFT_MAX_DEFAULT = 300


class _Budget:
    def __init__(
        self,
        records_max: int | None,
        bytes_max: int | None,
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
        if self._records_max is not None and self._records >= self._records_max:
            return True

        if self._bytes_max is not None and self._bytes >= self._bytes_max:
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

        if self._bytes_max is not None:
            if self._bytes + bytes_ > self._bytes_max:
                return False

        return True

    def consume(self, records: int, bytes_: int) -> None:
        self._records += records
        self._bytes += bytes_


def _record_size(record: SyncRecord) -> int:
    import json  # noqa: PLC0415

    return len(json.dumps(record.to_dict(), ensure_ascii=True))


def _cursor_last(records: dict[str, SyncRecord]) -> dict[str, Any] | None:
    if not records:
        return None

    key_last = list(records.keys())[-1]
    record_last = records[key_last]

    return {
        'key': key_last,
        'sequence': record_last.sequence,
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
        foreign_key_columns: dict[str, list[tuple[str, str]]] | None = None,
        identity_field: str = 'id',
        lock: SyncLock | None = None,
        on_complete: Callable[[DatabaseResult], None] | None = None,
        on_phase: Callable[[SyncPhase], None] | None = None,
        payload_bytes_max: int | None = None,
        payload_records_max: int | None = None,
        peer_node_id: str | None = None,
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

        if transport is not None and not peer_node_id:
            message = (
                'peer_node_id is required when transport is set '
                '(client mode)'
            )

            raise InvalidParameterError(message)

        if peer_node_id is not None and peer_node_id == node_id:
            message = (
                f'peer_node_id must differ from node_id '
                f'(both are {node_id!r})'
            )

            raise InvalidParameterError(message)

        self._batch_bytes = batch_bytes
        self._batch_size = batch_size
        self._clock = clock
        self._clock_drift_max = clock_drift_max
        self._errored_keys: dict[str, set[str]] = defaultdict(set)
        self._foreign_key_columns = foreign_key_columns or {}
        self._graph = graph
        self._identity_field = identity_field
        self._lock = lock
        self._node_id = node_id
        self._on_complete = on_complete
        self._on_phase = on_phase
        self._payload_bytes_max = payload_bytes_max
        self._payload_records_max = payload_records_max
        self._peer_node_id = peer_node_id or ''
        self._progress = progress
        self._reconciler = reconciler or PayloadReconciler()
        self._storage = storage
        self._transaction = transaction
        self._transport = transport

    def _advance_clock(self, manifest: SyncManifest) -> None:
        wall = self._max_applied_timestamp(manifest)

        if wall:
            self._clock.receive(wall)

    def _apply_incoming(
        self,
        payloads: list[ModelPayload],
        peer_sequence: int,
        peer_node_id: str,
        result: DatabaseResult,
        sequence_max: int,
        records_max: int | None = None,
        bytes_max: int | None = None,
        after_keys: dict[str, Any] | None = None,
    ) -> tuple[list[ModelPayload], bool, dict[str, Any], int]:
        incoming_by_label = {
            payload.model_label: payload
            for payload in payloads
        }

        resolved_after_keys = after_keys or {}
        response_payloads: list[ModelPayload] = []
        response_cursors: dict[str, Any] = {}
        budget = _Budget(records_max, bytes_max)
        has_more = False
        response_sequence_max = peer_sequence
        skipped_sequence_min: int | None = None

        for model_label in self._graph.sync_order():
            incoming_payload = incoming_by_label.get(model_label)

            if incoming_payload is not None:
                response_payload, truncated, skipped_sequence_first = (
                    self._process_model(
                        incoming_payload,
                        peer_sequence,
                        peer_node_id,
                        result,
                        budget=budget,
                        sequence_max=sequence_max,
                    )
                )

                if truncated:
                    has_more = True

                    if response_payload.records:
                        cursor = _cursor_last(
                            response_payload.records,
                        )

                        if cursor:
                            response_cursors[model_label] = cursor

                    if (
                        model_label not in response_cursors
                        and skipped_sequence_first is not None
                    ):
                        if (
                            skipped_sequence_min is None
                            or skipped_sequence_first < skipped_sequence_min
                        ):
                            skipped_sequence_min = skipped_sequence_first

                if response_payload.records or response_payload.deletes:
                    response_payloads.append(response_payload)

                    for record in response_payload.records.values():
                        if record.sequence > response_sequence_max:
                            response_sequence_max = record.sequence

                continue

            if budget.exhausted:
                probe = self._storage.get_changed_since(
                    model_label,
                    peer_sequence,
                    peer_node_id,
                    sequence_max=sequence_max,
                    limit=1,
                )

                probe_sequence_first = None

                if probe:
                    has_more = True

                    record_first = next(iter(probe.values()))
                    probe_sequence_first = record_first.sequence

                    if (
                        skipped_sequence_min is None
                        or probe_sequence_first < skipped_sequence_min
                    ):
                        skipped_sequence_min = probe_sequence_first

                continue

            cursor = resolved_after_keys.get(model_label)

            local_payload, truncated, skipped_sequence_first = (
                self._collect_local_only_payload(
                    model_label,
                    peer_sequence,
                    peer_node_id,
                    budget,
                    cursor=cursor,
                    sequence_max=sequence_max,
                )
            )

            if truncated:
                has_more = True

                if local_payload is not None:
                    cursor_out = _cursor_last(local_payload.records)

                    if cursor_out:
                        response_cursors[model_label] = cursor_out

                if (
                    model_label not in response_cursors
                    and skipped_sequence_first is not None
                ):
                    if (
                        skipped_sequence_min is None
                        or skipped_sequence_first < skipped_sequence_min
                    ):
                        skipped_sequence_min = skipped_sequence_first

            if local_payload is not None:
                response_payloads.append(local_payload)

                for record in local_payload.records.values():
                    if record.sequence > response_sequence_max:
                        response_sequence_max = record.sequence

        if skipped_sequence_min is not None:
            response_sequence_max = min(response_sequence_max, skipped_sequence_min - 1)

        return response_payloads, has_more, response_cursors, response_sequence_max

    def _apply_reconciliation(
        self,
        model_label: str,
        reconciliation: ReconciliationResult,
        result: DatabaseResult,
        origin_node: str,
    ) -> UpsertResult:
        cascade_errors = self._cascade_drop_foreign_key_orphans(
            model_label,
            reconciliation,
        )

        if cascade_errors:
            reconciliation.errors.extend(cascade_errors)

        upsert_result = UpsertResult()

        if reconciliation.to_upsert:
            upsert_result = self._storage.upsert_many(
                model_label,
                reconciliation.to_upsert,
                origin_node,
            )

        for error in upsert_result.errors:
            self._errored_keys[model_label].add(error.key)

        for error in cascade_errors:
            self._errored_keys[model_label].add(error.key)

        if reconciliation.to_clear_tombstones:
            excluded = upsert_result.skipped | {
                error.key
                for error in upsert_result.errors
            }

            clearable = reconciliation.to_clear_tombstones - excluded

            if clearable:
                self._storage.clear_tombstones(model_label, clearable)

        if reconciliation.to_delete:
            self._storage.delete_many(
                model_label,
                reconciliation.to_delete,
                origin_node,
            )

        self._merge_into_result(
            model_label,
            reconciliation,
            upsert_result,
            result,
        )

        return upsert_result

    def _apply_response(
        self,
        response: SyncManifest,
        result: DatabaseResult,
    ) -> list[int]:
        known = self._graph.known_models()

        ordered = self._order_payloads([
            payload for payload in response.payloads
            if payload.model_label in known
        ])

        failed_sequences: list[int] = []

        for payload in ordered:
            errors_before = len(result.errors)

            self._process_model(
                payload,
                response.peer_sequence,
                response.node_id,
                result,
                budget=None,
                sequence_max=None,
            )

            new_errors = result.errors[errors_before:]

            for error in new_errors:
                record = payload.records.get(error.key)

                if record is not None:
                    failed_sequences.append(record.sequence)

        return failed_sequences

    def _cascade_drop_foreign_key_orphans(
        self,
        model_label: str,
        reconciliation: ReconciliationResult,
    ) -> list[Error]:
        foreign_keys = self._foreign_key_columns.get(model_label)

        if not foreign_keys or not reconciliation.to_upsert:
            return []

        cascade_errors: list[Error] = []
        keys_to_drop: list[str] = []

        for key, record in reconciliation.to_upsert.items():
            for attribute_name, target_label in foreign_keys:
                value = record.data.get(attribute_name)

                if value is None:
                    continue

                errored_parents = self._errored_keys.get(target_label)

                if not errored_parents:
                    continue

                if str(value) in errored_parents:
                    cascade_errors.append(Error(
                        key=key,
                        message=(
                            f'Cascading failure: {model_label} record {key} '
                            f'references errored parent '
                            f'{target_label}={value!r} via {attribute_name}'
                        ),
                    ))

                    keys_to_drop.append(key)
                    break

        for key in keys_to_drop:
            reconciliation.to_upsert.pop(key, None)
            reconciliation.response_records.pop(key, None)

        return cascade_errors

    def _collect(
        self,
        local_sequence_pushed: int,
        peer_node_id: str,
        sequence_max: int,
        limit: int | None = None,
        bytes_limit: int | None = None,
        after_keys: dict[str, Any] | None = None,
    ) -> SyncManifest:
        resolved_after_keys = after_keys or {}
        budget = _Budget(limit, bytes_limit)
        payloads: list[ModelPayload] = []
        cursors: dict[str, Any] = {}
        has_more = False
        sent_sequence_max = local_sequence_pushed
        skipped_sequence_min: int | None = None

        for model_label in self._graph.sync_order():
            if budget.exhausted:
                probe = self._storage.get_changed_since(
                    model_label,
                    local_sequence_pushed,
                    peer_node_id,
                    sequence_max=sequence_max,
                    limit=1,
                )

                if probe:
                    has_more = True

                    record_first = next(iter(probe.values()))

                    if (
                        skipped_sequence_min is None
                        or record_first.sequence < skipped_sequence_min
                    ):
                        skipped_sequence_min = record_first.sequence

                continue

            cursor = resolved_after_keys.get(model_label)

            payload, truncated, skipped_sequence_first = (
                self._collect_local_only_payload(
                    model_label,
                    local_sequence_pushed,
                    peer_node_id,
                    budget,
                    cursor=cursor,
                    sequence_max=sequence_max,
                )
            )

            if truncated:
                has_more = True

                if payload is not None:
                    payload_cursor = _cursor_last(payload.records)

                    if payload_cursor:
                        cursors[model_label] = payload_cursor

                if (
                    model_label not in cursors
                    and skipped_sequence_first is not None
                ):
                    if (
                        skipped_sequence_min is None
                        or skipped_sequence_first < skipped_sequence_min
                    ):
                        skipped_sequence_min = skipped_sequence_first

            if payload is not None:
                payloads.append(payload)

                for record in payload.records.values():
                    if record.sequence > sent_sequence_max:
                        sent_sequence_max = record.sequence

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

        if skipped_sequence_min is not None:
            sent_sequence_max = min(sent_sequence_max, skipped_sequence_min - 1)

        if has_more:
            outgoing_local_sequence = sent_sequence_max
        else:
            outgoing_local_sequence = sequence_max

        manifest = SyncManifest(
            node_id=self._node_id,
            peer_sequence=0,
            local_sequence=outgoing_local_sequence,
            node_time=int(time.time()),
            payloads=payloads,
            has_more=has_more,
        )

        manifest.after_keys = cursors

        return manifest

    def _collect_local_only_payload(
        self,
        model_label: str,
        sequence: int,
        peer_node_id: str,
        budget: _Budget,
        cursor: dict[str, Any] | None = None,
        sequence_max: int | None = None,
    ) -> tuple[ModelPayload | None, bool, int | None]:
        record_limit = budget.remaining_records

        fetch_limit = (
            None if record_limit is None
            else record_limit + 1
        )

        effective_seq = sequence
        effective_after_key = None

        if cursor:
            effective_seq = cursor.get('sequence', sequence)
            effective_after_key = cursor.get('key')

        records = self._storage.get_changed_since(
            model_label,
            effective_seq,
            peer_node_id,
            sequence_max=sequence_max,
            limit=fetch_limit,
            after_key=effective_after_key,
        )

        truncated = False
        skipped_sequence_first: int | None = None

        if (
            record_limit is not None
            and len(records) > record_limit
        ):
            items = list(records.items())

            if record_limit == 0:
                skipped_sequence_first = items[0][1].sequence

            records = dict(items[:record_limit])

            truncated = True

        accepted: dict[str, SyncRecord] = {}

        for key, record in records.items():
            record_bytes = _record_size(record)

            if not budget.can_fit(1, record_bytes):
                truncated = True

                if not accepted and skipped_sequence_first is None:
                    skipped_sequence_first = record.sequence

                break

            accepted[key] = record
            budget.consume(1, record_bytes)

        deletes = self._storage.get_deletes_since(
            model_label,
            sequence,
            peer_node_id,
            sequence_max=sequence_max,
        )

        if not accepted and not deletes:
            return None, truncated, skipped_sequence_first

        return ModelPayload(
            model_label=model_label,
            records=accepted,
            deletes=deletes,
        ), truncated, skipped_sequence_first

    def _commit(
        self,
        peer_sequence_old: int,
        local_sequence_pushed_old: int,
        sent_max_sequence: int,
        sent_has_more: bool,
        sent_counter_at_start: int,
        response: SyncManifest,
        result: DatabaseResult,
        server_cursors: dict[str, Any] | None = None,
        collect_cursors: dict[str, Any] | None = None,
    ) -> None:
        with self._transaction():
            failed_sequences = self._apply_response(response, result)
            self._flush_deferred_backfill()

            if failed_sequences:
                safe_seq = min(failed_sequences) - 1

                logger.warning(
                    'Sync apply failed for %d record(s); '
                    'holding peer_sequence at %d '
                    '(response.local_sequence=%d). '
                    'Failed records will be retried on next sync.',
                    len(failed_sequences),
                    safe_seq,
                    response.local_sequence,
                )
            else:
                safe_seq = response.local_sequence

            new_peer_sequence = max(
                peer_sequence_old,
                safe_seq,
            )

            if sent_has_more:
                new_local_sequence_pushed = max(
                    local_sequence_pushed_old,
                    sent_max_sequence,
                )
            else:
                new_local_sequence_pushed = max(
                    local_sequence_pushed_old,
                    sent_counter_at_start,
                )

            if new_peer_sequence < peer_sequence_old:
                message = (
                    f'New peer_sequence {new_peer_sequence} precedes '
                    f'old peer_sequence {peer_sequence_old}'
                )

                raise SyncAbortedError(message)

            if new_local_sequence_pushed < local_sequence_pushed_old:
                message = (
                    f'New local_sequence_pushed {new_local_sequence_pushed} '
                    f'precedes old {local_sequence_pushed_old}'
                )

                raise SyncAbortedError(message)

            persisted_cursors: dict[str, Any] = {}

            if server_cursors:
                persisted_cursors.update({
                    f'server:{key}': value
                    for key, value in server_cursors.items()
                })

            if collect_cursors:
                persisted_cursors.update({
                    f'collect:{key}': value
                    for key, value in collect_cursors.items()
                })

            self._storage.save_checkpoint(
                self._peer_node_id,
                new_peer_sequence,
                new_local_sequence_pushed,
                after_keys=persisted_cursors or None,
            )

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

        if self._peer_node_id and response.node_id != self._peer_node_id:
            message = (
                f'Configured peer_node_id {self._peer_node_id!r} '
                f'does not match server-reported node_id '
                f'{response.node_id!r}'
            )

            raise SyncAbortedError(message)

        return response

    def _finalize(self, result: DatabaseResult) -> None:
        if self._on_complete:
            self._on_complete(result)

        for error in result.errors:
            logger.warning(
                'Sync error [%s]: %s',
                error.key,
                error.message,
            )

        skipped_total = sum(
            len(keys) for keys in result.skipped.values()
        )

        if skipped_total:
            logger.info(
                'Sync skipped %d record(s) due to staleness',
                skipped_total,
            )

    def _flush_deferred_backfill(self) -> None:
        flush = getattr(
            self._storage,
            'flush_deferred_backfill',
            None,
        )

        if flush is not None:
            flush()

    def _get_local_only_changes(
        self,
        model_label: str,
        sequence: int,
        peer_node_id: str,
        incoming_keys: set[str],
        sequence_max: int | None = None,
        limit: int | None = None,
    ) -> tuple[dict[str, SyncRecord], bool, int | None]:
        fetch_limit = (
            None if limit is None
            else limit + len(incoming_keys) + 1
        )

        all_changes = self._storage.get_changed_since(
            model_label,
            sequence,
            peer_node_id,
            sequence_max=sequence_max,
            limit=fetch_limit,
        )

        result = {
            key: record
            for key, record in all_changes.items()
            if key not in incoming_keys
        }

        truncated = False
        skipped_sequence_first: int | None = None

        if limit is not None and len(result) > limit:
            items = list(result.items())

            if limit == 0:
                skipped_sequence_first = items[0][1].sequence

            result = dict(items[:limit])

            truncated = True

        return result, truncated, skipped_sequence_first

    def _log_sync_summary(
        self,
        result: DatabaseResult,
    ) -> None:
        pushed_total = sum(len(keys) for keys in result.pushed.values())
        created_total = sum(len(keys) for keys in result.created.values())
        applied_total = sum(len(keys) for keys in result.applied.values())
        deleted_total = sum(len(keys) for keys in result.deleted.values())
        conflicts_total = sum(len(keys) for keys in result.conflicts.values())
        compatible_total = sum(len(keys) for keys in result.compatible.values())
        skipped_total = sum(len(keys) for keys in result.skipped.values())

        logger.info(
            'Database sync complete: '
            '%d pushed, %d created, %d applied, %d deleted, '
            '%d conflicts, %d compatible, %d skipped, %d errors',
            pushed_total,
            created_total,
            applied_total,
            deleted_total,
            conflicts_total,
            compatible_total,
            skipped_total,
            len(result.errors),
        )

    def _has_concurrent_writes_for_peer(
        self,
        peer_node_id: str,
        sequence_threshold: int,
    ) -> bool:
        for model_label in self._graph.sync_order():
            records = self._storage.get_changed_since(
                model_label,
                sequence_threshold,
                peer_node_id,
                limit=1,
            )

            if records:
                return True

            deletes = self._storage.get_deletes_since(
                model_label,
                sequence_threshold,
                peer_node_id,
            )

            if deletes:
                return True

        return False

    @contextmanager
    def _managed_session(
        self,
        result: DatabaseResult | None = None,
    ) -> Iterator[str]:
        session_id = ''

        if self._lock:
            session_id = self._lock.acquire(self._node_id, self._peer_node_id)

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
        self,
        manifest: SyncManifest,
    ) -> int:
        timestamp_max = 0

        for payload in manifest.payloads:
            for record in payload.records.values():
                timestamp_max = max(
                    timestamp_max,
                    record.sync_field_last_modified,
                )

            for tombstone_timestamp in payload.deletes.values():
                timestamp_max = max(
                    timestamp_max,
                    tombstone_timestamp,
                )

        return timestamp_max

    def _merge_into_result(
        self,
        model_label: str,
        reconciliation: ReconciliationResult,
        upsert_result: UpsertResult,
        result: DatabaseResult,
    ) -> None:
        skipped = upsert_result.skipped
        errored = {error.key for error in upsert_result.errors}
        excluded = skipped | errored

        for key in reconciliation.created_keys:
            if key not in excluded:
                result.created[model_label].append(key)

        for key in reconciliation.compatible_keys:
            if key not in excluded:
                result.applied[model_label].append(key)
                result.compatible[model_label].append(key)

        for key in reconciliation.conflict_keys:
            if key not in excluded:
                result.conflicts[model_label].append(key)

        for key in reconciliation.to_delete:
            result.deleted[model_label].append(key)

        for key in skipped:
            result.skipped[model_label].append(key)

        result.errors.extend(reconciliation.errors)
        result.errors.extend(upsert_result.errors)
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
        sequence: int,
        peer_node_id: str,
        result: DatabaseResult,
        budget: _Budget | None = None,
        sequence_max: int | None = None,
    ) -> tuple[ModelPayload, bool, int | None]:
        all_incoming_keys = (
            set(payload.records) |
            set(payload.deletes)
        )

        local_records = self._storage.get_records(
            payload.model_label,
            all_incoming_keys,
        )

        local_tombstones = self._storage.get_tombstones(
            payload.model_label,
            set(payload.records),
        )

        reconciliation = self._reconciler.reconcile(
            payload,
            local_records,
            local_tombstones,
        )

        upsert_result = self._apply_reconciliation(
            payload.model_label,
            reconciliation,
            result,
            origin_node=peer_node_id,
        )

        errored_keys = {error.key for error in upsert_result.errors}
        excluded_keys = upsert_result.skipped | errored_keys

        response_records: dict[str, SyncRecord] = {
            key: record
            for key, record in reconciliation.response_records.items()
            if key not in excluded_keys
        }

        truncated = False

        local_only_limit = (
            None if budget is None
            else budget.remaining_records
        )

        local_only, local_truncated, sequence_skipped_first_local = (
            self._get_local_only_changes(
                payload.model_label,
                sequence,
                peer_node_id,
                all_incoming_keys,
                sequence_max=sequence_max,
                limit=local_only_limit,
            )
        )

        if local_truncated:
            truncated = True

        skipped_sequence_first = sequence_skipped_first_local

        for key, record in local_only.items():
            if key in response_records:
                continue

            record_bytes = _record_size(record)

            if budget is not None and not budget.can_fit(1, record_bytes):
                truncated = True

                if not response_records and skipped_sequence_first is None:
                    skipped_sequence_first = record.sequence

                break

            response_records[key] = record

            if budget is not None:
                budget.consume(1, record_bytes)

        deletes = self._storage.get_deletes_since(
            payload.model_label,
            sequence,
            peer_node_id,
            sequence_max=sequence_max,
        )

        return ModelPayload(
            model_label=payload.model_label,
            records=response_records,
            deletes=deletes,
        ), truncated, skipped_sequence_first

    def _record_pushed(
        self,
        manifest: SyncManifest,
        result: DatabaseResult,
    ) -> None:
        for payload in manifest.payloads:
            for key in payload.records:
                result.pushed[payload.model_label].append(key)

            for key in payload.deletes:
                result.pushed[payload.model_label].append(key)

    def _report_phase(
        self,
        phase: SyncPhase,
        session_id: str,
    ) -> None:
        if self._lock and session_id:
            try:
                self._lock.update_phase(session_id, phase)
            except Exception:
                logger.exception(
                    'Failed to update sync phase '
                    'for session %s',
                    session_id,
                )

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

    def _reset_errored_keys(self) -> None:
        self._errored_keys = defaultdict(set)

    def _stamp_unstamped_records(self) -> None:
        stamp = getattr(
            self._storage,
            'stamp_unstamped_records',
            None,
        )

        if stamp is not None:
            stamp(
                clock=self._clock,
                model_order=self._graph.sync_order(),
            )

    def _validate_clock(self, manifest: SyncManifest) -> int:
        if self._clock_drift_max is None:
            return 0

        if not manifest.node_time:
            return 0

        local_time = int(time.time())
        drift = abs(local_time - manifest.node_time)

        if drift > self._clock_drift_max:
            message = (
                f'Clock drift between {self._node_id} '
                f'and {manifest.node_id} is {drift}s, '
                f'exceeds clock_drift_max='
                f'{self._clock_drift_max}s. '
                f'Ensure NTP is enabled on both nodes, '
                f'or set clock_drift_max=None to disable.'
            )

            raise ClockDriftError(message)

        if drift > 0:
            logger.debug('Clock drift: %ds', drift)

        return drift

    def _validate_incoming_models(
        self,
        manifest: SyncManifest,
        result: DatabaseResult,
    ) -> list[ModelPayload]:
        known = self._graph.known_models()
        valid: list[ModelPayload] = []

        for payload in manifest.payloads:
            if payload.model_label not in known:
                for key in payload.records:
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
        self,
        manifest: SyncManifest,
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

        self._reset_errored_keys()
        self._stamp_unstamped_records()

        self._validate_manifest(incoming)
        self._validate_clock(incoming)

        valid_payloads = self._validate_incoming_models(
            incoming,
            result,
        )

        peer_node_id = incoming.node_id

        with self._transaction():
            if self._lock:
                self._lock.hold_global()
                self._lock.hold(self._node_id, peer_node_id)

            counter_at_start = (
                self._storage.get_sequence_allocator().current()
            )

            response_payloads, has_more, after_keys, response_sequence_max = (
                self._apply_incoming(
                    valid_payloads,
                    incoming.peer_sequence,
                    peer_node_id,
                    result,
                    sequence_max=counter_at_start,
                    records_max=self._batch_size,
                    bytes_max=self._batch_bytes,
                    after_keys=incoming.after_keys,
                )
            )

            self._flush_deferred_backfill()

        self._advance_clock(incoming)

        if has_more:
            outgoing_local_sequence = response_sequence_max
        else:
            outgoing_local_sequence = counter_at_start

        response = SyncManifest(
            node_id=self._node_id,
            peer_sequence=incoming.local_sequence,
            local_sequence=outgoing_local_sequence,
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

        if not self._peer_node_id:
            message = (
                'peer_node_id is required for sync(). '
                'Configure it on the engine.'
            )

            raise InvalidParameterError(message)

        result = DatabaseResult()

        self._reset_errored_keys()

        persisted = self._storage.get_after_keys(self._peer_node_id)

        server_cursors: dict[str, Any] = {
            key.removeprefix('server:'): value
            for key, value in persisted.items()
            if key.startswith('server:')
        }

        collect_cursors: dict[str, Any] = {
            key.removeprefix('collect:'): value
            for key, value in persisted.items()
            if key.startswith('collect:')
        }

        iteration = 0

        with self._managed_session(result) as session_id:
            self._stamp_unstamped_records()

            while True:
                iteration += 1

                self._enter_phase(
                    SyncPhase.COLLECTING,
                    session_id,
                    SyncStage.VALIDATE,
                )

                checkpoint = self._storage.get_checkpoint(self._peer_node_id)
                peer_sequence = checkpoint.peer_sequence
                local_sequence_pushed = checkpoint.local_sequence_pushed

                counter_at_start = (
                    self._storage.get_sequence_allocator().current()
                )

                manifest = self._collect(
                    local_sequence_pushed,
                    self._peer_node_id,
                    sequence_max=counter_at_start,
                    limit=self._batch_size,
                    bytes_limit=self._batch_bytes,
                    after_keys=collect_cursors,
                )

                manifest.peer_sequence = peer_sequence
                manifest.after_keys = server_cursors
                manifest.checksum = manifest.compute_checksum()

                sent_max_sequence = manifest.local_sequence
                sent_has_more = manifest.has_more

                self._record_pushed(manifest, result)

                self._enter_phase(
                    SyncPhase.EXCHANGING,
                    session_id,
                    SyncStage.CLASSIFY,
                )

                response = self._exchange_and_validate(manifest)

                self._enter_phase(
                    SyncPhase.RECONCILING,
                    session_id,
                    SyncStage.MUTATE,
                )

                if manifest.has_more:
                    collect_cursors = {}

                    for payload in manifest.payloads:
                        cursor = _cursor_last(payload.records)

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
                        peer_sequence,
                        local_sequence_pushed,
                        sent_max_sequence,
                        sent_has_more,
                        counter_at_start,
                        response,
                        result,
                        server_cursors=server_cursors,
                        collect_cursors=collect_cursors,
                    )

                self._advance_clock(response)

                converged = (
                    not manifest.has_more
                    and not response.has_more
                )

                if dry_run:
                    break

                if converged:
                    exchanged = (
                        any(payload.records or payload.deletes for payload in manifest.payloads)
                        or any(payload.records or payload.deletes for payload in response.payloads)
                    )

                    if not exchanged:
                        break

            self._enter_phase(SyncPhase.COMPLETE, session_id)
            self._finalize(result)

        # self._log_sync_summary(result)

        return result
