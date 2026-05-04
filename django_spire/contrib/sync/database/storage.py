from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.contrib.sync.database.record import SyncRecord


class CheckpointStore(Protocol):
    def get_after_keys(self, node_id: str) -> dict[str, dict[str, int | str]]: ...
    def get_checkpoint(self, node_id: str) -> int: ...
    def save_checkpoint(self, node_id: str, timestamp: int, after_keys: dict[str, dict[str, int | str]] | None = None) -> None: ...


class RecordReader(Protocol):
    def get_changed_since(self, model_label: str, timestamp: int, limit: int | None = None, after_key: str | None = None) -> dict[str, SyncRecord]: ...
    def get_deletes_since(self, model_label: str, timestamp: int) -> dict[str, int]: ...
    def get_records(self, model_label: str, keys: set[str]) -> dict[str, SyncRecord]: ...


class RecordWriter(Protocol):
    def delete_many(self, model_label: str, deletes: dict[str, int]) -> None: ...
    def upsert_many(self, model_label: str, records: dict[str, SyncRecord]) -> set[str]: ...


class DatabaseSyncStorage(CheckpointStore, RecordReader, RecordWriter, Protocol):
    pass
