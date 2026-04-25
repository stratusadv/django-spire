from __future__ import annotations

from django_spire.contrib.sync.database.conflict import (
    ConflictType,
    FieldConflict,
    FieldTimestampWins,
    LocalWins,
    RecordConflict,
    RemoteWins,
    ResolutionSource,
)
from django_spire.contrib.sync.database.record import SyncRecord


_DEFAULT_LOCAL = {'id': '1', 'name': 'local', 'value': 10}
_DEFAULT_REMOTE = {'id': '1', 'name': 'remote', 'value': 20}

_SENTINEL = object()


def _make_conflict(
    conflict_type: ConflictType = ConflictType.BOTH_MODIFIED,
    local_data: dict | object = _SENTINEL,
    remote_data: dict | object = _SENTINEL,
    local_timestamps: dict | None = None,
    remote_timestamps: dict | None = None,
    field_conflicts: list[FieldConflict] | None = None,
) -> RecordConflict:
    local = None

    if local_data is not None:
        data = dict(_DEFAULT_LOCAL) if local_data is _SENTINEL else local_data
        local = SyncRecord(key='1', data=data, timestamps=local_timestamps or {})

    remote = None

    if remote_data is not None:
        data = dict(_DEFAULT_REMOTE) if remote_data is _SENTINEL else remote_data
        remote = SyncRecord(key='1', data=data, timestamps=remote_timestamps or {})

    return RecordConflict(
        key='1',
        model_label='app.Model',
        conflict_type=conflict_type,
        field_conflicts=field_conflicts or [],
        local=local,
        remote=remote,
    )


def test_ftw_picks_higher_timestamp_per_field() -> None:
    conflict = _make_conflict(
        local_timestamps={'id': 100, 'name': 100, 'value': 200},
        remote_timestamps={'id': 100, 'name': 200, 'value': 100},
    )

    resolution = FieldTimestampWins().resolve(conflict)

    assert resolution.source == ResolutionSource.MERGED
    assert resolution.record is not None
    assert resolution.record.data['name'] == 'remote'
    assert resolution.record.data['value'] == 10
    assert resolution.record.timestamps['name'] == 200
    assert resolution.record.timestamps['value'] == 200


def test_ftw_local_wins_on_equal_timestamp() -> None:
    conflict = _make_conflict(
        local_timestamps={'name': 100},
        remote_timestamps={'name': 100},
    )

    resolution = FieldTimestampWins().resolve(conflict)

    assert resolution.record is not None
    assert resolution.record.data['name'] == 'local'


def test_ftw_delete_vs_modify_keeps_local() -> None:
    conflict = _make_conflict(
        conflict_type=ConflictType.DELETE_VS_MODIFY,
        remote_data=None,
    )

    resolution = FieldTimestampWins().resolve(conflict)

    assert resolution.source == ResolutionSource.LOCAL
    assert resolution.record is not None
    assert resolution.record.data['name'] == 'local'


def test_ftw_modify_vs_delete_keeps_remote() -> None:
    conflict = _make_conflict(
        conflict_type=ConflictType.MODIFY_VS_DELETE,
        local_data=None,
    )

    resolution = FieldTimestampWins().resolve(conflict)

    assert resolution.source == ResolutionSource.REMOTE
    assert resolution.record is not None
    assert resolution.record.data['name'] == 'remote'


def test_ftw_excludes_meta_fields() -> None:
    conflict = _make_conflict(
        local_data={
            'id': '1',
            'name': 'local',
            'sync_field_timestamps': {},
            'sync_field_last_modified': 999,
        },
        remote_data={
            'id': '1',
            'name': 'remote',
            'sync_field_timestamps': {},
            'sync_field_last_modified': 888,
        },
        local_timestamps={'name': 100},
        remote_timestamps={'name': 200},
    )

    resolution = FieldTimestampWins().resolve(conflict)

    assert resolution.record is not None
    assert 'sync_field_timestamps' not in resolution.record.data
    assert 'sync_field_last_modified' not in resolution.record.data


def test_ftw_custom_exclude() -> None:
    conflict = _make_conflict(
        local_data={'id': '1', 'name': 'local', 'internal': 'x'},
        remote_data={'id': '1', 'name': 'remote', 'internal': 'y'},
        local_timestamps={'name': 100, 'internal': 300},
        remote_timestamps={'name': 200, 'internal': 100},
    )

    resolution = FieldTimestampWins(exclude_fields={'internal'}).resolve(conflict)

    assert resolution.record is not None
    assert 'internal' not in resolution.record.data


def test_ftw_preserves_field_conflicts() -> None:
    fc = FieldConflict(
        field_name='name',
        local_value='local',
        remote_value='remote',
        local_timestamp=100,
        remote_timestamp=200,
    )

    conflict = _make_conflict(
        local_timestamps={'name': 100},
        remote_timestamps={'name': 200},
        field_conflicts=[fc],
    )

    resolution = FieldTimestampWins().resolve(conflict)

    assert len(resolution.field_conflicts) == 1
    assert resolution.field_conflicts[0].field_name == 'name'


def test_local_wins_returns_local_record() -> None:
    conflict = _make_conflict(
        local_timestamps={'name': 50},
    )

    resolution = LocalWins().resolve(conflict)

    assert resolution.source == ResolutionSource.LOCAL
    assert resolution.record is not None
    assert resolution.record.data['name'] == 'local'
    assert resolution.delete is False


def test_local_wins_modify_vs_delete() -> None:
    conflict = _make_conflict(
        conflict_type=ConflictType.MODIFY_VS_DELETE,
    )

    resolution = LocalWins().resolve(conflict)

    assert resolution.source == ResolutionSource.LOCAL
    assert resolution.record is None
    assert resolution.delete is True


def test_local_wins_preserves_field_conflicts() -> None:
    fc = FieldConflict(
        field_name='value',
        local_value=10,
        remote_value=20,
        local_timestamp=100,
        remote_timestamp=200,
    )

    conflict = _make_conflict(field_conflicts=[fc])

    resolution = LocalWins().resolve(conflict)

    assert len(resolution.field_conflicts) == 1


def test_remote_wins_returns_remote_record() -> None:
    conflict = _make_conflict(
        remote_timestamps={'name': 50},
    )

    resolution = RemoteWins().resolve(conflict)

    assert resolution.source == ResolutionSource.REMOTE
    assert resolution.record is not None
    assert resolution.record.data['name'] == 'remote'
    assert resolution.delete is False


def test_remote_wins_delete_vs_modify() -> None:
    conflict = _make_conflict(
        conflict_type=ConflictType.DELETE_VS_MODIFY,
    )

    resolution = RemoteWins().resolve(conflict)

    assert resolution.source == ResolutionSource.REMOTE
    assert resolution.record is None
    assert resolution.delete is True


def test_remote_wins_preserves_field_conflicts() -> None:
    fc = FieldConflict(
        field_name='value',
        local_value=10,
        remote_value=20,
        local_timestamp=100,
        remote_timestamp=200,
    )

    conflict = _make_conflict(field_conflicts=[fc])

    resolution = RemoteWins().resolve(conflict)

    assert len(resolution.field_conflicts) == 1
