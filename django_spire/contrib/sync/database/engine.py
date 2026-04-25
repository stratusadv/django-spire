from __future__ import annotations

import logging
import time

from contextlib import contextmanager, nullcontext
from typing import Any, Callable, Iterator, TYPE_CHECKING

from django_spire.contrib.sync.core.enums import SyncPhase, SyncStage, SyncStatus
from django_spire.contrib.sync.core.exceptions import (
    ClockDriftError,
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
    from contextlib import AbstractContextManager

    from django_spire.contrib.sync.core.clock import HybridLogicalClock
    from django_spire.contrib.sync.database.graph import DependencyGraph
    from django_spire.contrib.sync.database.lock import SyncLock
    from django_spire.contrib.sync.database.storage import DatabaseSyncStorage
    from django_spire.contrib.sync.database.transport.base import Transport


logger = logging.getLogger(__name__)

CLOCK_DRIFT_MAX_DEFAULT = 300


class DatabaseEngine:
    def __init__(
        self,
        storage: DatabaseSyncStorage,
        graph: DependencyGraph,
        clock: HybridLogicalClock,
        lock: SyncLock | None = None,
        reconciler: PayloadReconciler | None = None,
        transport: Transport | None = None,
        identity_field: str = 'id',
        node_id: str = '',
        clock_drift_max: int | None = CLOCK_DRIFT_MAX_DEFAULT,
        payload_records_max: int | None = None,
        transaction: Callable[[], AbstractContextManager[Any]] | None = None,
        on_complete: Callable[[DatabaseResult], None] | None = None,
        on_phase: Callable[[SyncPhase], None] | None = None,
        progress: Callable[[SyncStage, int, int], None] | None = None,
    ) -> None:
        self._clock = clock
        self._clock_drift_max = clock_drift_max
        self._graph = graph
        self._identity_field = identity_field
        self._lock = lock
        self._node_id = node_id
        self._on_complete = on_complete
        self._on_phase = on_phase
        self._payload_records_max = payload_records_max
        self._progress = progress
        self._reconciler = reconciler or PayloadReconciler()
        self._storage = storage
        self._transaction = transaction or nullcontext
        self._transport = transport

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
                    self._lock.release(session_id, status, result=result)
                except Exception:
                    logger.exception(
                        'Failed to release sync lock for node %s',
                        self._node_id,
                    )

    def _advance_clock(self, manifest: SyncManifest) -> None:
        wall = max(
            self._max_applied_timestamp(manifest),
            manifest.checkpoint,
        )

        if wall:
            self._clock.receive(wall)

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

            skipped = self._storage.upsert_many(model_label, records)

        if reconciliation.to_delete:
            self._storage.delete_many(model_label, reconciliation.to_delete)

        self._merge_into_result(
            model_label, reconciliation, skipped, result,
        )

    def _check_clock_drift(self, remote_time: int) -> int:
        local_time = int(time.time())
        drift = abs(local_time - remote_time)

        if self._clock_drift_max is not None and drift > self._clock_drift_max:
            message = (
                f'Clock drift of {drift}s exceeds threshold of '
                f'{self._clock_drift_max}s. Local time: {local_time}, '
                f'remote time: {remote_time}. '
                f'Ensure NTP is enabled '
                f'on both nodes, or set clock_drift_max=None to disable.'
            )
            raise ClockDriftError(message)

        if drift > 0:
            logger.debug('Clock drift: %ds', drift)

        return drift

    def _collect(self, checkpoint: int) -> SyncManifest:
        payloads: list[ModelPayload] = []
        records_total = 0

        for model_label in self._graph.sync_order():
            records = self._storage.get_changed_since(model_label, checkpoint)
            records_total += len(records)

            if records:
                payloads.append(ModelPayload(
                    model_label=model_label,
                    records=records,
                ))

        if (
            self._payload_records_max is not None
            and records_total > self._payload_records_max
        ):
            message = (
                f'Collected {records_total} records exceeds '
                f'payload_records_max={self._payload_records_max}. '
                f'Sync more frequently or increase the limit.'
            )
            raise PayloadLimitError(message)

        return SyncManifest(
            node_id=self._node_id,
            checkpoint=checkpoint,
            node_time=int(time.time()),
            payloads=payloads,
        )

    def _compute_safe_checkpoint(
        self,
        old_checkpoint: int,
        new_checkpoint: int,
        sent_snapshot: dict[str, dict[str, int]],
        received_snapshot: dict[str, dict[str, int]],
    ) -> int:
        unsent_min = new_checkpoint

        for model_label in self._graph.sync_order():
            changes = self._storage.get_changed_since(
                model_label, old_checkpoint,
            )

            sent_lms = sent_snapshot.get(model_label, {})
            received_lms = received_snapshot.get(model_label, {})

            for key, record in changes.items():
                sent_lm = sent_lms.get(key)
                received_lm = received_lms.get(key)

                if sent_lm is not None and record.sync_field_last_modified == sent_lm:
                    continue

                if received_lm is not None and record.sync_field_last_modified == received_lm:
                    continue

                unsent_min = min(unsent_min, record.sync_field_last_modified)

        if unsent_min < new_checkpoint:
            return max(unsent_min - 1, old_checkpoint)

        return new_checkpoint

    def _extract_record_snapshot(
        self,
        manifest: SyncManifest,
    ) -> dict[str, dict[str, int]]:
        snapshot: dict[str, dict[str, int]] = {}

        for payload in manifest.payloads:
            snapshot[payload.model_label] = {
                key: record.sync_field_last_modified
                for key, record in payload.records.items()
            }

        return snapshot

    def _finalize(self, result: DatabaseResult) -> None:
        if self._on_complete:
            self._on_complete(result)

        for error in result.errors:
            logger.warning('Sync error [%s]: %s', error.key, error.message)

    def _get_local_only_changes(
        self,
        model_label: str,
        checkpoint: int,
        incoming_keys: set[str],
    ) -> dict[str, SyncRecord]:
        all_changes = self._storage.get_changed_since(
            model_label, checkpoint,
        )

        return {
            key: record
            for key, record in all_changes.items()
            if key not in incoming_keys
        }

    def _max_applied_timestamp(self, manifest: SyncManifest) -> int:
        timestamp_max = 0

        for payload in manifest.payloads:
            for record in payload.records.values():
                timestamp_max = max(timestamp_max, record.sync_field_last_modified)

            for tombstone_ts in payload.deletes.values():
                timestamp_max = max(timestamp_max, tombstone_ts)

        return timestamp_max

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
        position = {label: index for index, label in enumerate(order)}

        return sorted(
            payloads,
            key=lambda p: position.get(p.model_label, len(position)),
        )

    def _process_model(
        self,
        payload: ModelPayload,
        checkpoint: int,
        result: DatabaseResult,
        received_at: int = 0,
    ) -> ModelPayload:
        all_incoming_keys = set(payload.records) | set(payload.deletes)

        local_records = self._storage.get_records(
            payload.model_label, all_incoming_keys,
        )

        reconciliation = self._reconciler.reconcile(
            payload, local_records, checkpoint,
        )

        self._apply_reconciliation(
            payload.model_label, reconciliation, result,
            received_at=received_at,
        )

        local_only = self._get_local_only_changes(
            payload.model_label, checkpoint, all_incoming_keys,
        )

        response_records = {**reconciliation.response_records, **local_only}

        return ModelPayload(
            model_label=payload.model_label,
            records=response_records,
        )

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

    def _validate_clock(self, manifest: SyncManifest) -> None:
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
                    'Ignoring unknown model %r from node %s',
                    payload.model_label,
                    incoming.node_id,
                )

                for key in set(payload.records) | set(payload.deletes):
                    result.errors.append(Error(
                        key=key,
                        message=(
                            f'Unknown model: {payload.model_label!r}'
                        ),
                    ))

                continue

            valid.append(payload)

        return valid

    def _validate_manifest(self, manifest: SyncManifest) -> None:
        if not manifest.checksum:
            message = 'Manifest is missing a checksum'
            raise ManifestChecksumError(message)

        if manifest.checksum != manifest.compute_checksum():
            message = 'Manifest checksum verification failed'
            raise ManifestChecksumError(message)

    def apply_incoming(
        self,
        payloads: list[ModelPayload],
        checkpoint: int,
        result: DatabaseResult,
        received_at: int = 0,
    ) -> list[ModelPayload]:
        incoming_by_label = {
            payload.model_label: payload for payload in payloads
        }

        response_payloads: list[ModelPayload] = []

        for model_label in self._graph.sync_order():
            payload = incoming_by_label.get(model_label)

            if payload is not None:
                response_payload = self._process_model(
                    payload, checkpoint, result,
                    received_at=received_at,
                )

                if response_payload.records or response_payload.deletes:
                    response_payloads.append(response_payload)
            else:
                local_changes = self._storage.get_changed_since(
                    model_label, checkpoint,
                )

                if local_changes:
                    response_payloads.append(ModelPayload(
                        model_label=model_label,
                        records=local_changes,
                    ))

        return response_payloads

    def apply_response(
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

    def _apply_response_records(
        self,
        payload: ModelPayload,
        result: DatabaseResult,
    ) -> None:
        skipped = self._storage.upsert_many(
            payload.model_label, payload.records,
        )

        applied_keys = set(payload.records.keys()) - skipped
        result.applied[payload.model_label].extend(applied_keys)

        for key in skipped:
            result.skipped[payload.model_label].append(key)

    def _apply_response_deletes(
        self,
        payload: ModelPayload,
        result: DatabaseResult,
    ) -> None:
        existing = self._storage.get_records(
            payload.model_label, set(payload.deletes.keys()),
        )

        to_delete: dict[str, int] = {}

        for key, tombstone_ts in payload.deletes.items():
            local = existing.get(key)

            if local is None or local.sync_field_last_modified <= tombstone_ts:
                to_delete[key] = tombstone_ts
            else:
                logger.info(
                    'Skipping delete for %s:%s: local modified after tombstone',
                    payload.model_label,
                    key,
                )
                result.skipped[payload.model_label].append(key)

        if to_delete:
            self._storage.delete_many(payload.model_label, to_delete)

            for key in to_delete:
                result.deleted[payload.model_label].append(key)

    def process(
        self,
        incoming: SyncManifest,
    ) -> tuple[SyncManifest, DatabaseResult]:
        result = DatabaseResult()

        self._validate_manifest(incoming)
        self._validate_clock(incoming)

        valid_payloads = self._validate_incoming_models(incoming, result)

        with self._transaction():
            now = self._clock.now()
            response_payloads = self.apply_incoming(
                valid_payloads, incoming.checkpoint, result,
                received_at=now,
            )

        response = SyncManifest(
            node_id=self._node_id,
            checkpoint=now,
            node_time=int(time.time()),
            payloads=response_payloads,
        )

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

        with self._managed_session(result) as session_id:
            self._report_phase(SyncPhase.COLLECTING, session_id)
            self._report_progress(SyncStage.VALIDATE, 0, 1)

            checkpoint = self._storage.get_checkpoint(self._node_id)
            manifest = self._collect(checkpoint)
            sent_snapshot = self._extract_record_snapshot(manifest)

            for payload in manifest.payloads:
                keys = list(payload.records.keys())

                if keys:
                    result.pushed[payload.model_label] = keys

            self._report_phase(SyncPhase.EXCHANGING, session_id)
            self._report_progress(SyncStage.CLASSIFY, 0, 1)

            response = self._transport.exchange(manifest)

            self._validate_manifest(response)
            self._validate_clock(response)

            received_snapshot = self._extract_record_snapshot(response)

            self._report_phase(SyncPhase.RECONCILING, session_id)
            self._report_progress(SyncStage.MUTATE, 0, 1)

            if not dry_run:
                self._report_phase(SyncPhase.COMMITTING, session_id)

                with self._transaction():
                    self.apply_response(response, result)

                    safe_checkpoint = self._compute_safe_checkpoint(
                        checkpoint,
                        response.checkpoint,
                        sent_snapshot,
                        received_snapshot,
                    )

                    self._storage.save_checkpoint(
                        self._node_id,
                        safe_checkpoint,
                    )

            self._report_phase(SyncPhase.COMPLETE, session_id)
            self._finalize(result)

        logger.info(
            'Database sync complete: %d models pushed, %d models applied, '
            '%d models with conflicts, %d errors',
            len(result.pushed),
            len(result.applied),
            len(result.conflicts),
            len(result.errors),
        )

        return result
