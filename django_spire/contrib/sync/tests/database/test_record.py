from __future__ import annotations

import pytest

from django_spire.contrib.sync.core.exceptions import RecordFieldError
from django_spire.contrib.sync.database.record import SyncRecord


def test_from_dict_valid() -> None:
    record = SyncRecord.from_dict(
        '1',
        {'data': {'name': 'Alice'}, 'timestamps': {'name': 100}},
    )

    assert record.key == '1'
    assert record.data == {'name': 'Alice'}
    assert record.timestamps == {'name': 100}


def test_from_dict_defaults() -> None:
    record = SyncRecord.from_dict('1', {})

    assert record.key == '1'
    assert record.data == {}
    assert record.timestamps == {}


def test_from_dict_rejects_non_dict_data() -> None:
    with pytest.raises(RecordFieldError, match='data'):
        SyncRecord.from_dict(
            '1',
            {'data': 'not-a-dict', 'timestamps': {}},
        )


def test_from_dict_rejects_non_dict_timestamps() -> None:
    with pytest.raises(RecordFieldError, match='timestamps'):
        SyncRecord.from_dict(
            '1',
            {'data': {}, 'timestamps': [1, 2, 3]},
        )


def test_from_dict_rejects_non_int_timestamp_value() -> None:
    with pytest.raises(RecordFieldError, match='timestamp'):
        SyncRecord.from_dict(
            '1',
            {'data': {'name': 'x'}, 'timestamps': {'name': 'not-an-int'}},
        )


def test_from_dict_rejects_bool_timestamp_value() -> None:
    with pytest.raises(RecordFieldError, match='timestamp'):
        SyncRecord.from_dict(
            '1',
            {'data': {'name': 'x'}, 'timestamps': {'name': True}},
        )


def test_from_dict_rejects_non_string_timestamp_key() -> None:
    with pytest.raises(RecordFieldError, match='timestamp'):
        SyncRecord.from_dict(
            '1',
            {'data': {}, 'timestamps': {123: 100}},
        )


def test_sync_field_last_modified_empty_timestamps() -> None:
    record = SyncRecord(key='1', data={}, timestamps={})

    assert record.sync_field_last_modified == 0


def test_sync_field_last_modified_uses_max_timestamp() -> None:
    record = SyncRecord(
        key='1',
        data={'name': 'Alice', 'value': 10},
        timestamps={'name': 100, 'value': 300},
    )

    assert record.sync_field_last_modified == 300


def test_sync_field_last_modified_uses_received_at_when_higher() -> None:
    record = SyncRecord(
        key='1',
        data={},
        timestamps={'name': 100},
        received_at=500,
    )

    assert record.sync_field_last_modified == 500


def test_received_at_not_serialized() -> None:
    record = SyncRecord(
        key='1',
        data={'name': 'Alice'},
        timestamps={'name': 100},
        received_at=500,
    )

    data = record.to_dict()

    assert 'received_at' not in data
