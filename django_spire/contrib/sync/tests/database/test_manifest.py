from __future__ import annotations

import pytest

from django_spire.contrib.sync.core.exceptions import ManifestFieldError
from django_spire.contrib.sync.database.manifest import (
    ModelPayload,
    SyncManifest,
)
from django_spire.contrib.sync.database.record import SyncRecord


def test_model_payload_to_dict() -> None:
    payload = ModelPayload(
        model_label='app.Model',
        records={
            '1': SyncRecord(key='1', data={'name': 'Alice'}, timestamps={}),
        },
        deletes={'2': 500},
    )

    data = payload.to_dict()

    assert data['model_label'] == 'app.Model'
    assert '1' in data['records']
    assert data['records']['1']['data']['name'] == 'Alice'
    assert data['deletes'] == {'2': 500}


def test_model_payload_from_dict() -> None:
    data = {
        'model_label': 'app.Model',
        'records': {
            '1': {'data': {'name': 'Alice'}, 'timestamps': {}},
        },
        'deletes': {'3': 800},
    }

    payload = ModelPayload.from_dict(data)

    assert payload.model_label == 'app.Model'
    assert len(payload.records) == 1
    assert '1' in payload.records
    assert payload.deletes == {'3': 800}


def test_model_payload_round_trip() -> None:
    original = ModelPayload(
        model_label='app.Model',
        records={
            '1': SyncRecord(key='1', data={'name': 'Alice'}, timestamps={}),
        },
        deletes={'2': 500, '3': 700},
    )

    restored = ModelPayload.from_dict(original.to_dict())

    assert restored.model_label == original.model_label
    assert set(restored.records.keys()) == set(original.records.keys())
    assert restored.records['1'].data == original.records['1'].data
    assert restored.deletes == original.deletes


def test_model_payload_from_dict_defaults() -> None:
    data = {'model_label': 'app.Model'}

    payload = ModelPayload.from_dict(data)

    assert payload.records == {}
    assert payload.deletes == {}


def test_model_payload_rejects_non_dict_deletes() -> None:
    data = {
        'model_label': 'app.Model',
        'deletes': ['1', '2'],
    }

    with pytest.raises(ManifestFieldError, match='deletes'):
        ModelPayload.from_dict(data)


def test_model_payload_rejects_non_int_tombstone() -> None:
    data = {
        'model_label': 'app.Model',
        'deletes': {'1': 'not-an-int'},
    }

    with pytest.raises(ManifestFieldError, match='tombstone'):
        ModelPayload.from_dict(data)


def test_sync_manifest_to_dict() -> None:
    manifest = SyncManifest(
        node_id='tablet-1',
        checkpoint=1000,
        node_time=1001,
        payloads=[
            ModelPayload(
                model_label='app.Model',
                records={
                    '1': SyncRecord(key='1', data={'name': 'Alice'}, timestamps={}),
                },
            ),
        ],
    )

    data = manifest.to_dict()

    assert data['node_id'] == 'tablet-1'
    assert data['checkpoint'] == 1000
    assert data['node_time'] == 1001
    assert len(data['payloads']) == 1
    assert data['payloads'][0]['model_label'] == 'app.Model'


def test_sync_manifest_from_dict() -> None:
    data = {
        'node_id': 'server',
        'checkpoint': 500,
        'node_time': 501,
        'payloads': [
            {
                'model_label': 'app.Model',
                'records': {
                    '1': {'data': {'name': 'Alice'}, 'timestamps': {}},
                },
            },
        ],
    }

    manifest = SyncManifest.from_dict(data)

    assert manifest.node_id == 'server'
    assert manifest.checkpoint == 500
    assert manifest.node_time == 501
    assert len(manifest.payloads) == 1


def test_sync_manifest_round_trip() -> None:
    original = SyncManifest(
        node_id='tablet-1',
        checkpoint=1000,
        node_time=1001,
        payloads=[
            ModelPayload(
                model_label='app.Model',
                records={
                    '1': SyncRecord(key='1', data={'name': 'Alice'}, timestamps={}),
                },
                deletes={'2': 600},
            ),
            ModelPayload(
                model_label='app.Other',
                records={},
                deletes={'5': 700},
            ),
        ],
    )

    restored = SyncManifest.from_dict(original.to_dict())

    assert restored.node_id == original.node_id
    assert restored.checkpoint == original.checkpoint
    assert restored.node_time == original.node_time
    assert len(restored.payloads) == 2
    assert set(restored.payloads[0].records.keys()) == set(original.payloads[0].records.keys())
    assert restored.payloads[1].deletes == original.payloads[1].deletes


def test_sync_manifest_from_dict_defaults() -> None:
    data = {
        'node_id': 'server',
        'checkpoint': 0,
    }

    manifest = SyncManifest.from_dict(data)

    assert manifest.node_time == 0
    assert manifest.payloads == []


def test_sync_manifest_rejects_empty_node_id() -> None:
    data = {
        'node_id': '',
        'checkpoint': 0,
    }

    with pytest.raises(ManifestFieldError, match='non-empty'):
        SyncManifest.from_dict(data)


def test_sync_manifest_rejects_negative_checkpoint() -> None:
    data = {
        'node_id': 'tablet',
        'checkpoint': -1,
    }

    with pytest.raises(ManifestFieldError, match='non-negative'):
        SyncManifest.from_dict(data)


def test_sync_manifest_rejects_duplicate_model_label() -> None:
    data = {
        'node_id': 'tablet',
        'checkpoint': 0,
        'payloads': [
            {'model_label': 'app.Model'},
            {'model_label': 'app.Model'},
        ],
    }

    with pytest.raises(ManifestFieldError, match='duplicate'):
        SyncManifest.from_dict(data)


def test_sync_manifest_verify_rejects_empty_checksum() -> None:
    manifest = SyncManifest(
        node_id='tablet',
        checkpoint=0,
        node_time=0,
        payloads=[],
    )

    assert manifest.verify() is False


def test_sync_manifest_verify_valid_checksum() -> None:
    manifest = SyncManifest(
        node_id='tablet',
        checkpoint=0,
        node_time=0,
        payloads=[],
    )
    manifest.checksum = manifest.compute_checksum()

    assert manifest.verify() is True


def test_sync_manifest_verify_tampered_checksum() -> None:
    manifest = SyncManifest(
        node_id='tablet',
        checkpoint=0,
        node_time=0,
        payloads=[],
    )
    manifest.checksum = 'deadbeef'

    assert manifest.verify() is False


def test_sync_manifest_to_dict_includes_checksum() -> None:
    manifest = SyncManifest(
        node_id='tablet',
        checkpoint=100,
        node_time=101,
        payloads=[],
    )

    data = manifest.to_dict()

    assert data['checksum'] != ''

    restored = SyncManifest.from_dict(data)

    assert restored.verify() is True
