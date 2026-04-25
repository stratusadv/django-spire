from __future__ import annotations

from typing import Any

from django_spire.contrib.sync.database.manifest import ModelPayload, SyncManifest
from django_spire.contrib.sync.database.record import SyncRecord


def make_record(
    key: str,
    data: dict[str, Any] | None = None,
    timestamps: dict[str, int] | None = None,
    received_at: int = 0,
) -> SyncRecord:
    return SyncRecord(
        key=key,
        data=data if data is not None else {'id': key},
        timestamps=timestamps or {},
        received_at=received_at,
    )


def make_payload(
    model_label: str,
    records: dict[str, SyncRecord] | None = None,
    deletes: dict[str, int] | None = None,
) -> ModelPayload:
    return ModelPayload(
        model_label=model_label,
        records=records or {},
        deletes=deletes or {},
    )


def make_manifest(
    node_id: str = 'remote',
    checkpoint: int = 0,
    node_time: int = 0,
    payloads: list[ModelPayload] | None = None,
    sign: bool = True,
) -> SyncManifest:
    manifest = SyncManifest(
        node_id=node_id,
        checkpoint=checkpoint,
        node_time=node_time,
        payloads=payloads or [],
    )

    if sign:
        manifest.checksum = manifest.compute_checksum()

    return manifest
