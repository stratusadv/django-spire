from __future__ import annotations

import logging

from typing import Any, TYPE_CHECKING

from django_spire.contrib.sync.django.sequence import SyncSequenceAllocator
from django_spire.contrib.sync.django.storage.checkpoint import DjangoCheckpointStore
from django_spire.contrib.sync.django.storage.reader import DjangoRecordReader
from django_spire.contrib.sync.django.storage.writer import DjangoRecordWriter

if TYPE_CHECKING:
    from django_spire.contrib.sync.core.clock import HybridLogicalClock
    from django_spire.contrib.sync.database.storage import UpsertResult
    from django_spire.contrib.sync.database.record import SyncRecord
    from django_spire.contrib.sync.database.storage import (
        CheckpointPosition,
        CheckpointStore,
        RecordReader,
        RecordWriter,
        SequenceAllocator,
    )
    from django_spire.contrib.sync.django.graph import DeferredForeignKey
    from django_spire.contrib.sync.django.mixin import SyncableMixin


logger = logging.getLogger(__name__)

_BATCH_SIZE_MAX = 5_000


class DjangoSyncStorage:
    def __init__(
        self,
        models: list[type[SyncableMixin]],
        identity_field: str = 'id',
        batch_size_max: int = _BATCH_SIZE_MAX,
        checkpoint_store: CheckpointStore | None = None,
        deferred_fks: list[DeferredForeignKey] | None = None,
        record_reader: RecordReader | None = None,
        record_writer: RecordWriter | None = None,
        sequence_allocator: SequenceAllocator | None = None,
    ) -> None:
        self._checkpoint_store = checkpoint_store or DjangoCheckpointStore()

        self._record_reader = record_reader or DjangoRecordReader(
            models=models,
            identity_field=identity_field,
        )

        self._record_writer = record_writer or DjangoRecordWriter(
            models=models,
            identity_field=identity_field,
            batch_size_max=batch_size_max,
            deferred_fks=deferred_fks,
        )

        self._sequence_allocator = (
            sequence_allocator or SyncSequenceAllocator()
        )

    def clear_tombstones(
        self,
        model_label: str,
        keys: set[str],
    ) -> None:
        self._record_writer.clear_tombstones(model_label, keys)

    def delete_many(
        self,
        model_label: str,
        deletes: dict[str, int],
        origin_node: str,
    ) -> None:
        self._record_writer.delete_many(
            model_label,
            deletes,
            origin_node,
        )

    def flush_deferred_backfill(self) -> None:
        self._record_writer.flush_deferred_backfill()

    def get_after_keys(self, peer_node_id: str) -> dict[str, Any]:
        return self._checkpoint_store.get_after_keys(peer_node_id)

    def get_changed_since(
        self,
        model_label: str,
        sequence: int,
        peer_node_id: str,
        sequence_max: int | None = None,
        limit: int | None = None,
        after_key: str | None = None,
    ) -> dict[str, SyncRecord]:
        return self._record_reader.get_changed_since(
            model_label,
            sequence,
            peer_node_id,
            sequence_max=sequence_max,
            limit=limit,
            after_key=after_key,
        )

    def get_deletes_since(
        self,
        model_label: str,
        sequence: int,
        peer_node_id: str,
        sequence_max: int | None = None,
    ) -> dict[str, int]:
        return self._record_reader.get_deletes_since(
            model_label,
            sequence,
            peer_node_id,
            sequence_max=sequence_max,
        )

    def get_checkpoint(self, peer_node_id: str) -> CheckpointPosition:
        return self._checkpoint_store.get_checkpoint(peer_node_id)

    def get_records(
        self,
        model_label: str,
        keys: set[str],
    ) -> dict[str, SyncRecord]:
        return self._record_reader.get_records(model_label, keys)

    def get_sequence_allocator(self) -> SequenceAllocator:
        return self._sequence_allocator

    def get_syncable_models(self) -> list[str]:
        return self._record_reader.get_syncable_models()

    def get_tombstones(
        self,
        model_label: str,
        keys: set[str],
    ) -> dict[str, int]:
        return self._record_reader.get_tombstones(model_label, keys)

    def save_checkpoint(
        self,
        peer_node_id: str,
        peer_sequence: int,
        local_sequence_pushed: int,
        after_keys: dict[str, Any] | None = None,
    ) -> None:
        self._checkpoint_store.save_checkpoint(
            peer_node_id,
            peer_sequence,
            local_sequence_pushed,
            after_keys=after_keys,
        )

    def stamp_unstamped_records(
        self,
        clock: HybridLogicalClock,
        model_order: list[str] | None = None,
    ) -> None:
        count = self._record_writer.stamp_unstamped_records(
            clock=clock,
            model_order=model_order,
        )

        if count:
            logger.info(
                'Pre-sync stamping complete: %d records',
                count,
            )

    def upsert_many(
        self,
        model_label: str,
        records: dict[str, SyncRecord],
        origin_node: str,
    ) -> UpsertResult:
        return self._record_writer.upsert_many(
            model_label,
            records,
            origin_node,
        )
