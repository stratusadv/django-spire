from __future__ import annotations

from dataclasses import dataclass, field

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Any


@dataclass
class CellData:
    fields: list[FieldDisplay]
    title: str


@dataclass
class ClassifiedRow:
    cloud_cell: CellData | None
    cloud_object: Any
    difference_count: int
    difference_fields: list[str]
    id: str
    kind: str
    merged_cell: MergedCellData | None
    model: str
    resolution: ConflictLogEntry | None
    tablet_cell: CellData | None
    tablet_object: Any


@dataclass
class CloudDatabaseView:
    sections: list[CloudSection]
    total_records: int


@dataclass
class CloudRecord:
    fields: list[CloudRecordField]
    id: str
    sync_field_last_modified: HybridLogicalClockDecoded
    title: str


@dataclass
class CloudRecordField:
    full_value: str
    name: str
    timestamp: HybridLogicalClockDecoded
    value: str


@dataclass
class CloudSection:
    model_name: str
    record_count: int
    records: list[CloudRecord]


@dataclass
class ConflictLogEntry:
    conflict_type: str = ''
    field_conflicts: list[FieldConflictDetail] = field(default_factory=list)
    key: str = ''
    model_label: str = ''
    resolution_source: str = ''


@dataclass
class FieldConflictDetail:
    field_name: str = ''
    local_timestamp: int = 0
    local_value: Any = ''
    remote_timestamp: int = 0
    remote_value: Any = ''
    winner: str = ''


@dataclass
class FieldDisplay:
    full_value: str
    is_diff: bool
    name: str
    outcome: str
    timestamp: HybridLogicalClockDecoded
    value: str


@dataclass
class HybridLogicalClockDecoded:
    counter: int
    human: str
    raw: str
    wall_ms: int


@dataclass
class MergedCloudRecord:
    fields: list[MergedCloudRecordField]
    id: str
    model: str
    title: str


@dataclass
class MergedCloudRecordField:
    name: str
    source: str
    value: str


@dataclass
class MergedCellData:
    fields: list[FieldDisplay]
    outcome: str
    title: str


@dataclass
class ModelConfig:
    fields: tuple[str, ...]
    foreign_key_fields: tuple[str, ...]
    model: type


@dataclass
class SerializedSyncResult:
    applied: dict[str, list[str]] = field(default_factory=dict)
    compatible: dict[str, list[str]] = field(default_factory=dict)
    conflict_log: list[ConflictLogEntry] = field(default_factory=list)
    conflicts: dict[str, list[str]] = field(default_factory=dict)
    created: dict[str, list[str]] = field(default_factory=dict)
    deleted: dict[str, list[str]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    skipped: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class SyncCounts:
    cloud_only: int = 0
    conflict: int = 0
    match: int = 0
    tablet_only: int = 0


@dataclass
class SyncPerformResult:
    strategy: str
    sync_order: list[str]
    tablet_count: int
    tablets: dict[str, TabletSyncData]


@dataclass
class TabletSyncData:
    cloud_record_count: int
    cloud_result: SerializedSyncResult
    tablet_record_count: int
    tablet_result: SerializedSyncResult


@dataclass
class VerificationField:
    cloud_value: str
    matched: bool
    name: str
    tablet_value: str


@dataclass
class VerificationRecord:
    fields: list[VerificationField]
    id: str
    status: str
    title: str


@dataclass
class VerificationResult:
    tablet_sections: dict[str, list[VerificationSection]]
    total_matched: int
    total_mismatched: int
    total_records: int
    verified: bool


@dataclass
class VerificationSection:
    matched: int
    mismatched: int
    model_name: str
    record_count: int
    records: list[VerificationRecord]
