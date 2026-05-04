from __future__ import annotations

from django_spire.contrib.sync.database.tracker import FieldUpdateTracker


def test_no_changes_returns_empty() -> None:
    tracker = FieldUpdateTracker()
    fields = {'name': 'Alice', 'value': 10}

    tracker.snapshot(fields)

    assert tracker.get_dirty(fields) == set()


def test_detects_changed_field() -> None:
    tracker = FieldUpdateTracker()
    tracker.snapshot({'name': 'Alice', 'value': 10})

    dirty = tracker.get_dirty({'name': 'Alice', 'value': 20})

    assert dirty == {'value'}


def test_detects_multiple_changes() -> None:
    tracker = FieldUpdateTracker()
    tracker.snapshot({'name': 'Alice', 'value': 10})

    dirty = tracker.get_dirty({'name': 'Bob', 'value': 20})

    assert dirty == {'name', 'value'}


def test_detects_new_field() -> None:
    tracker = FieldUpdateTracker()
    tracker.snapshot({'name': 'Alice'})

    dirty = tracker.get_dirty({'name': 'Alice', 'value': 10})

    assert 'value' in dirty


def test_snapshot_resets_baseline() -> None:
    tracker = FieldUpdateTracker()
    tracker.snapshot({'name': 'Alice', 'value': 10})

    assert tracker.get_dirty({'name': 'Bob', 'value': 10}) == {'name'}

    tracker.snapshot({'name': 'Bob', 'value': 10})

    assert tracker.get_dirty({'name': 'Bob', 'value': 10}) == set()


def test_deep_copy_isolation() -> None:
    tracker = FieldUpdateTracker()
    fields = {'name': 'Alice', 'nested': [1, 2, 3]}

    tracker.snapshot(fields)
    fields['nested'].append(4)

    dirty = tracker.get_dirty({'name': 'Alice', 'nested': [1, 2, 3]})

    assert dirty == set()
