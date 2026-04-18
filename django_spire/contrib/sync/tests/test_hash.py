from __future__ import annotations

import pytest

from django_spire.contrib.sync.hash import RecordHasher


@pytest.fixture
def hasher() -> RecordHasher:
    return RecordHasher(identity_field='id')


def test_deterministic(hasher: RecordHasher) -> None:
    record = {'id': '1', 'name': 'Alpha', 'price': 100.0}

    assert hasher.hash(record) == hasher.hash(record)


def test_different_records(hasher: RecordHasher) -> None:
    a = {'id': '1', 'name': 'Alpha', 'price': 100.0}
    b = {'id': '1', 'name': 'Beta', 'price': 100.0}

    assert hasher.hash(a) != hasher.hash(b)


def test_ignores_identity_field(hasher: RecordHasher) -> None:
    a = {'id': '1', 'name': 'Alpha'}
    b = {'id': '2', 'name': 'Alpha'}

    assert hasher.hash(a) == hasher.hash(b)


def test_field_order_irrelevant(hasher: RecordHasher) -> None:
    a = {'id': '1', 'name': 'Alpha', 'price': 100.0}
    b = {'id': '1', 'price': 100.0, 'name': 'Alpha'}

    assert hasher.hash(a) == hasher.hash(b)


def test_compare_fields_subset() -> None:
    hasher = RecordHasher(identity_field='id', compare_fields=['price'])

    a = {'id': '1', 'name': 'Alpha', 'price': 100.0}
    b = {'id': '1', 'name': 'Beta', 'price': 100.0}

    assert hasher.hash(a) == hasher.hash(b)


def test_compare_fields_detects_change() -> None:
    hasher = RecordHasher(identity_field='id', compare_fields=['price'])

    a = {'id': '1', 'name': 'Alpha', 'price': 100.0}
    b = {'id': '1', 'name': 'Alpha', 'price': 200.0}

    assert hasher.hash(a) != hasher.hash(b)


def test_missing_field_raises() -> None:
    hasher = RecordHasher(identity_field='id', compare_fields=['missing'])

    with pytest.raises(ValueError, match='missing'):
        hasher.hash({'id': '1', 'name': 'Alpha'})


def test_handles_none(hasher: RecordHasher) -> None:
    a = {'id': '1', 'value': None}
    b = {'id': '1', 'value': 'something'}

    assert hasher.hash(a) != hasher.hash(b)


def test_handles_list(hasher: RecordHasher) -> None:
    a = {'id': '1', 'tags': ['a', 'b']}
    b = {'id': '1', 'tags': ['a', 'b', 'c']}

    assert hasher.hash(a) != hasher.hash(b)


def test_handles_nested_dict(hasher: RecordHasher) -> None:
    a = {'id': '1', 'meta': {'x': 1, 'y': 2}}
    b = {'id': '1', 'meta': {'y': 2, 'x': 1}}

    assert hasher.hash(a) == hasher.hash(b)


def test_type_sensitivity(hasher: RecordHasher) -> None:
    a = {'id': '1', 'value': 1}
    b = {'id': '1', 'value': '1'}

    assert hasher.hash(a) != hasher.hash(b)


def test_schema_tag_changes_with_compare_fields() -> None:
    h1 = RecordHasher(identity_field='id', compare_fields=['price'])
    h2 = RecordHasher(identity_field='id')

    record = {'id': '1', 'price': 100.0}

    assert h1.hash(record) != h2.hash(record)


def test_schema_tag_embedded_in_hash() -> None:
    hasher = RecordHasher(identity_field='id')
    record = {'id': '1', 'name': 'Alpha'}
    h = hasher.hash(record)

    assert ':' in h
    tag, body = h.split(':', 1)
    assert len(tag) == 8
    assert len(body) == 64


def test_non_serializable_raises(hasher: RecordHasher) -> None:
    record = {'id': '1', 'value': object()}

    with pytest.raises(TypeError, match='non-serializable'):
        hasher.hash(record)
