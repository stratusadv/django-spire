from __future__ import annotations

import string

from typing import Any

from hypothesis import strategies as st

from django_spire.contrib.sync.database.manifest import ModelPayload, SyncManifest
from django_spire.contrib.sync.database.record import SyncRecord


FIELD_NAMES = st.text(
    alphabet=string.ascii_lowercase,
    min_size=1,
    max_size=8,
)

FIELD_VALUES = st.one_of(
    st.integers(min_value=-10_000, max_value=10_000),
    st.text(alphabet=string.ascii_letters, min_size=0, max_size=20),
    st.booleans(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.none(),
)

TIMESTAMPS = st.integers(min_value=0, max_value=2**47)

DATA_DICTS = st.dictionaries(
    keys=FIELD_NAMES,
    values=FIELD_VALUES,
    min_size=1,
    max_size=6,
)

TIMESTAMP_DICTS = st.dictionaries(
    keys=FIELD_NAMES,
    values=TIMESTAMPS,
    min_size=1,
    max_size=6,
)


@st.composite
def sync_records(draw: st.DrawFn) -> SyncRecord:
    fields = draw(st.lists(
        FIELD_NAMES,
        min_size=1,
        max_size=6,
        unique=True,
    ))

    data = {'id': draw(st.text(alphabet=string.digits, min_size=1, max_size=5))}
    timestamps: dict[str, int] = {}

    for field in fields:
        data[field] = draw(FIELD_VALUES)
        timestamps[field] = draw(TIMESTAMPS)

    key = data['id']

    return SyncRecord(key=key, data=data, timestamps=timestamps)


@st.composite
def model_payloads(draw: st.DrawFn) -> ModelPayload:
    label = draw(st.text(
        alphabet=string.ascii_lowercase + '.',
        min_size=3,
        max_size=15,
    ))

    records: dict[str, SyncRecord] = {}
    num_records = draw(st.integers(min_value=0, max_value=3))

    for i in range(num_records):
        key = str(i)
        record = draw(sync_records())
        records[key] = SyncRecord(
            key=key,
            data=record.data,
            timestamps=record.timestamps,
        )

    delete_keys = draw(st.sets(
        st.text(alphabet=string.digits, min_size=1, max_size=3),
        max_size=3,
    ))

    delete_keys -= set(records.keys())

    deletes: dict[str, int] = {}

    for key in delete_keys:
        deletes[key] = draw(TIMESTAMPS)

    return ModelPayload(
        model_label=label,
        records=records,
        deletes=deletes,
    )


@st.composite
def sync_manifests(draw: st.DrawFn) -> SyncManifest:
    node_id = draw(st.text(
        alphabet=string.ascii_lowercase + '-',
        min_size=1,
        max_size=10,
    ))

    checkpoint = draw(st.integers(min_value=0, max_value=2**47))
    node_time = draw(st.integers(min_value=0, max_value=2**31))

    num_payloads = draw(st.integers(min_value=0, max_value=3))
    payloads: list[ModelPayload] = []
    seen_labels: set[str] = set()

    for _ in range(num_payloads):
        payload = draw(model_payloads())

        if payload.model_label in seen_labels:
            continue

        seen_labels.add(payload.model_label)
        payloads.append(payload)

    return SyncManifest(
        node_id=node_id,
        checkpoint=checkpoint,
        node_time=node_time,
        payloads=payloads,
    )


@st.composite
def field_conflict_pairs(
    draw: st.DrawFn,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, int], dict[str, int]]:
    fields = draw(st.lists(
        FIELD_NAMES,
        min_size=1,
        max_size=6,
        unique=True,
    ))

    local_data: dict[str, Any] = {'id': '1'}
    remote_data: dict[str, Any] = {'id': '1'}
    local_timestamps: dict[str, int] = {}
    remote_timestamps: dict[str, int] = {}

    for field in fields:
        local_data[field] = draw(FIELD_VALUES)
        remote_data[field] = draw(FIELD_VALUES)
        local_timestamps[field] = draw(TIMESTAMPS)
        remote_timestamps[field] = draw(TIMESTAMPS)

    return local_data, remote_data, local_timestamps, remote_timestamps


@st.composite
def reconciler_scenario(
    draw: st.DrawFn,
) -> tuple[dict[str, SyncRecord], dict[str, SyncRecord], int]:
    num_keys = draw(st.integers(min_value=1, max_value=8))
    checkpoint = draw(st.integers(min_value=50, max_value=500))

    fields = draw(st.lists(
        FIELD_NAMES,
        min_size=1,
        max_size=4,
        unique=True,
    ))

    local_records: dict[str, SyncRecord] = {}
    remote_records: dict[str, SyncRecord] = {}

    for i in range(num_keys):
        key = str(i)

        presence = draw(st.sampled_from(['both', 'local_only', 'remote_only']))

        has_local = presence in ('both', 'local_only')
        has_remote = presence in ('both', 'remote_only')

        if has_local:
            data: dict[str, Any] = {'id': key}
            timestamps: dict[str, int] = {}

            for field in fields:
                data[field] = draw(st.integers(min_value=0, max_value=1000))
                timestamps[field] = draw(st.integers(
                    min_value=1,
                    max_value=checkpoint * 4,
                ))

            local_records[key] = SyncRecord(
                key=key, data=data, timestamps=timestamps,
            )

        if has_remote:
            data = {'id': key}
            timestamps = {}

            for field in fields:
                data[field] = draw(st.integers(min_value=0, max_value=1000))
                timestamps[field] = draw(st.integers(
                    min_value=checkpoint + 1,
                    max_value=checkpoint * 4,
                ))

            remote_records[key] = SyncRecord(
                key=key, data=data, timestamps=timestamps,
            )

    return local_records, remote_records, checkpoint
