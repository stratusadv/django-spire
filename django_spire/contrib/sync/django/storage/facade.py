from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.sync.django.storage.checkpoint import DjangoCheckpointStore
from django_spire.contrib.sync.django.storage.reader import DjangoRecordReader
from django_spire.contrib.sync.django.storage.writer import DjangoRecordWriter

if TYPE_CHECKING:
    from django_spire.contrib.sync.database.record import SyncRecord
    from django_spire.contrib.sync.database.storage import (
        CheckpointStore,
        RecordReader,
        RecordWriter,
    )
    from django_spire.contrib.sync.django.mixin import SyncableMixin


_BATCH_SIZE_MAX = 5_000


class DjangoSyncStorage:
    def __init__(
        self,
        models: list[type[SyncableMixin]],
        identity_field: str = 'id',
        batch_size_max: int = _BATCH_SIZE_MAX,
        checkpoint_store: CheckpointStore | None = None,
        record_reader: RecordReader | None = None,
        record_writer: RecordWriter | None = None,
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
        )

    def delete_many(
        self,
        model_label: str,
        deletes: dict[str, int],
    ) -> None:
        self._record_writer.delete_many(model_label, deletes)

    def get_changed_since(
        self,
        model_label: str,
        timestamp: int,
    ) -> dict[str, SyncRecord]:
        return self._record_reader.get_changed_since(model_label, timestamp)

    def get_checkpoint(self, node_id: str) -> int:
        return self._checkpoint_store.get_checkpoint(node_id)

    def get_records(
        self,
        model_label: str,
        keys: set[str],
    ) -> dict[str, SyncRecord]:
        return self._record_reader.get_records(model_label, keys)

    def get_syncable_models(self) -> list[str]:
        return self._record_reader.get_syncable_models()

    def save_checkpoint(self, node_id: str, timestamp: int) -> None:
        self._checkpoint_store.save_checkpoint(node_id, timestamp)

    def upsert_many(
        self,
        model_label: str,
        records: dict[str, SyncRecord],
    ) -> set[str]:
        return self._record_writer.upsert_many(model_label, records)
