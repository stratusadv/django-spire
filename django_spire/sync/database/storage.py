from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, TYPE_CHECKING


if TYPE_CHECKING:
    from django_spire.sync.core.model import Error
    from django_spire.sync.database.record import SyncRecord


@dataclass
class UpsertResult:
    skipped: set[str] = field(default_factory=set)
    errors: list[Error] = field(default_factory=list)


@dataclass(frozen=True)
class SequenceRange:
    value_first: int
    value_last: int


@dataclass(frozen=True)
class CheckpointPosition:
    peer_sequence: int
    local_sequence_pushed: int


class SequenceAllocator(Protocol):
    def allocate(self, count: int = 1) -> SequenceRange: ...
    def current(self) -> int: ...


class CheckpointStore(Protocol):
    def get_after_keys(self, peer_node_id: str) -> dict[str, dict[str, int | str]]: ...
    def get_checkpoint(self, peer_node_id: str) -> CheckpointPosition: ...
    def save_checkpoint(
        self,
        peer_node_id: str,
        peer_sequence: int,
        local_sequence_pushed: int,
        after_keys: dict[str, dict[str, int | str]] | None = None,
    ) -> None: ...


class RecordReader(Protocol):
    def get_changed_since(
        self,
        model_label: str,
        sequence: int,
        peer_node_id: str,
        sequence_max: int | None = None,
        limit: int | None = None,
        after_key: str | None = None,
    ) -> dict[str, SyncRecord]: ...

    def get_deletes_since(
        self,
        model_label: str,
        sequence: int,
        peer_node_id: str,
        sequence_max: int | None = None,
    ) -> dict[str, int]: ...

    def get_records(
        self,
        model_label: str,
        keys: set[str],
    ) -> dict[str, SyncRecord]: ...

    def get_tombstones(
        self,
        model_label: str,
        keys: set[str],
    ) -> dict[str, int]: ...


class RecordWriter(Protocol):
    def clear_tombstones(
        self,
        model_label: str,
        keys: set[str],
    ) -> None: ...

    def delete_many(
        self,
        model_label: str,
        deletes: dict[str, int],
        origin_node: str,
    ) -> None: ...

    def upsert_many(
        self,
        model_label: str,
        records: dict[str, SyncRecord],
        origin_node: str,
    ) -> UpsertResult: ...


class DatabaseSyncStorage(
    CheckpointStore,
    RecordReader,
    RecordWriter,
    Protocol,
):
    def get_sequence_allocator(self) -> SequenceAllocator: ...
