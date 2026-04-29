from __future__ import annotations

import hashlib
import json

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

from django_spire.contrib.sync.core.exceptions import ManifestFieldError
from django_spire.contrib.sync.database.record import SyncRecord

if TYPE_CHECKING:
    from django_spire.contrib.sync.core.model import Error
    from django_spire.contrib.sync.database.conflict import (
        RecordConflict,
        ResolutionSource,
    )


_PAYLOADS_MAX = 1_000


@dataclass
class ModelPayload:
    model_label: str
    deletes: dict[str, int] = field(default_factory=dict)
    records: dict[str, SyncRecord] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelPayload:
        if not isinstance(data, dict):
            message = 'ModelPayload requires a dict'
            raise ManifestFieldError(message)

        model_label = data.get('model_label')

        if model_label is None:
            message = "ModelPayload requires 'model_label'"
            raise ManifestFieldError(message)

        if not isinstance(model_label, str):
            message = "'model_label' must be a string"
            raise ManifestFieldError(message)

        if not model_label:
            message = (
                "'model_label' must be a non-empty string"
            )
            raise ManifestFieldError(message)

        raw_records = data.get('records', {})

        if not isinstance(raw_records, dict):
            message = "'records' must be a dict"
            raise ManifestFieldError(message)

        raw_deletes = data.get('deletes', {})

        if not isinstance(raw_deletes, dict):
            message = (
                "'deletes' must be a dict of "
                "{key: tombstone_ts}"
            )

            raise ManifestFieldError(message)

        deletes: dict[str, int] = {}

        for key, tombstone in raw_deletes.items():
            if not isinstance(key, str):
                message = (
                    f"delete key {key!r} must be a string"
                )
                raise ManifestFieldError(message)

            if (
                not isinstance(tombstone, int)
                or isinstance(tombstone, bool)
            ):
                message = (
                    f"delete tombstone for {key!r} must be "
                    f"an int, got {type(tombstone).__name__}"
                )

                raise ManifestFieldError(message)

            if tombstone < 0:
                message = (
                    f"delete tombstone for {key!r} must be "
                    f"non-negative, got {tombstone}"
                )

                raise ManifestFieldError(message)

            if key in raw_records:
                message = (
                    f"key {key!r} present in both "
                    f"'records' and 'deletes'"
                )

                raise ManifestFieldError(message)

            deletes[key] = tombstone

        return cls(
            model_label=model_label,
            records={
                key: SyncRecord.from_dict(key, value)
                for key, value in raw_records.items()
            },
            deletes=deletes,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'deletes': dict(sorted(self.deletes.items())),
            'model_label': self.model_label,
            'records': {
                key: record.to_dict()
                for key, record in self.records.items()
            },
        }


@dataclass
class SyncManifest:
    node_id: str
    checkpoint: int
    checksum: str = ''
    node_time: int = 0
    payloads: list[ModelPayload] = field(
        default_factory=list,
    )

    def _serializable(self) -> dict[str, Any]:
        return {
            'checkpoint': self.checkpoint,
            'node_id': self.node_id,
            'node_time': self.node_time,
            'payloads': [
                payload.to_dict()
                for payload in self.payloads
            ],
        }

    def compute_checksum(self) -> str:
        body = json.dumps(
            self._serializable(),
            sort_keys=True,
            ensure_ascii=True,
        ).encode('utf-8')

        return hashlib.sha256(body).hexdigest()

    @classmethod
    def from_dict(
        cls, data: dict[str, Any],
    ) -> SyncManifest:
        node_id = data.get('node_id')
        checkpoint = data.get('checkpoint')

        if node_id is None:
            message = "SyncManifest requires 'node_id'"
            raise ManifestFieldError(message)

        if not isinstance(node_id, str):
            message = "'node_id' must be a string"
            raise ManifestFieldError(message)

        if not node_id:
            message = "'node_id' must be a non-empty string"
            raise ManifestFieldError(message)

        if checkpoint is None:
            message = "SyncManifest requires 'checkpoint'"
            raise ManifestFieldError(message)

        if (
            not isinstance(checkpoint, int)
            or isinstance(checkpoint, bool)
        ):
            message = "'checkpoint' must be an integer"
            raise ManifestFieldError(message)

        if checkpoint < 0:
            message = (
                f"'checkpoint' must be non-negative, "
                f"got {checkpoint}"
            )

            raise ManifestFieldError(message)

        node_time = data.get('node_time', 0)

        if (
            not isinstance(node_time, int)
            or isinstance(node_time, bool)
        ):
            message = "'node_time' must be an integer"
            raise ManifestFieldError(message)

        if node_time < 0:
            message = (
                f"'node_time' must be non-negative, "
                f"got {node_time}"
            )

            raise ManifestFieldError(message)

        raw_payloads = data.get('payloads', [])

        if not isinstance(raw_payloads, list):
            message = "'payloads' must be a list"
            raise ManifestFieldError(message)

        if len(raw_payloads) > _PAYLOADS_MAX:
            message = (
                f"'payloads' count {len(raw_payloads)} "
                f"exceeds limit of {_PAYLOADS_MAX}"
            )

            raise ManifestFieldError(message)

        payloads = [
            ModelPayload.from_dict(payload)
            for payload in raw_payloads
        ]

        seen_labels: set[str] = set()

        for payload in payloads:
            if payload.model_label in seen_labels:
                message = (
                    f"duplicate model_label "
                    f"{payload.model_label!r} in payloads"
                )

                raise ManifestFieldError(message)

            seen_labels.add(payload.model_label)

        return cls(
            node_id=node_id,
            checkpoint=checkpoint,
            checksum=data.get('checksum', ''),
            node_time=node_time,
            payloads=payloads,
        )

    def to_dict(self) -> dict[str, Any]:
        data = self._serializable()
        data['checksum'] = self.compute_checksum()

        return data

    def verify(self) -> bool:
        if not self.checksum:
            return False

        return self.checksum == self.compute_checksum()


@dataclass
class ConflictEntry:
    conflict: RecordConflict
    resolution_source: ResolutionSource


@dataclass
class DatabaseResult:
    applied: dict[str, list[str]] = field(
        default_factory=lambda: defaultdict(list),
    )
    compatible: dict[str, list[str]] = field(
        default_factory=lambda: defaultdict(list),
    )
    conflict_log: list[ConflictEntry] = field(
        default_factory=list,
    )
    conflicts: dict[str, list[str]] = field(
        default_factory=lambda: defaultdict(list),
    )
    created: dict[str, list[str]] = field(
        default_factory=lambda: defaultdict(list),
    )
    deleted: dict[str, list[str]] = field(
        default_factory=lambda: defaultdict(list),
    )
    errors: list[Error] = field(default_factory=list)
    pushed: dict[str, list[str]] = field(
        default_factory=lambda: defaultdict(list),
    )
    skipped: dict[str, list[str]] = field(
        default_factory=lambda: defaultdict(list),
    )

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0
