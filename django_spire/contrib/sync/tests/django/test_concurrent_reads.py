from __future__ import annotations

import threading
import time

import pytest

from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.tests.django.helpers import (
    make_named_record,
    make_storage,
    thread_safe,
)
from django_spire.contrib.sync.tests.models import SyncTestModel, SyncTestTag


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_reader_never_sees_torn_state_during_upsert() -> None:
    key = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'

    setup = make_storage()
    setup.upsert_many('sync_tests.SyncTestModel', {
        key: make_named_record(key, 'initial', 100, value=0),
    })

    stop = threading.Event()
    errors: list[Exception] = []
    bad_reads: list[dict] = []

    def writer() -> None:
        ts = 200
        while not stop.is_set():
            storage = make_storage()
            storage.upsert_many('sync_tests.SyncTestModel', {
                key: make_named_record(key, f'w-{ts}', ts, value=ts),
            })
            ts += 1

    def reader() -> None:
        while not stop.is_set():
            storage = make_storage()
            records = storage.get_records('sync_tests.SyncTestModel', {key})
            rec = records.get(key)
            if rec is None:
                bad_reads.append({'reason': 'missing'})
                continue
            name = rec.data.get('name')
            value = rec.data.get('value')
            if name == 'initial' and value == 0:
                continue
            if isinstance(name, str) and name.startswith('w-'):
                expected = int(name[2:])
                if value == expected:
                    continue
            bad_reads.append({'reason': 'torn', 'data': rec.data})

    writers = [
        threading.Thread(target=thread_safe(writer, errors))
        for _ in range(2)
    ]
    readers = [
        threading.Thread(target=thread_safe(reader, errors))
        for _ in range(3)
    ]

    for t in writers + readers:
        t.start()

    time.sleep(2.0)
    stop.set()

    for t in writers + readers:
        t.join(timeout=10)

    assert not errors, f'errors: {errors}'
    assert not bad_reads, f'torn reads: {bad_reads[:5]}'


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_get_changed_since_returns_consistent_snapshot() -> None:
    setup = make_storage()
    seed_records = {}

    for i in range(50):
        k = f'{i:08d}-0000-0000-0000-000000000000'
        seed_records[k] = make_named_record(k, f'seed-{i}', 100, value=i)

    setup.upsert_many('sync_tests.SyncTestModel', seed_records)

    stop = threading.Event()
    errors: list[Exception] = []
    counts: list[int] = []

    def writer() -> None:
        ts = 500
        while not stop.is_set():
            storage = make_storage()
            k = f'{ts % 50:08d}-0000-0000-0000-000000000000'
            storage.upsert_many('sync_tests.SyncTestModel', {
                k: make_named_record(k, f'upd-{ts}', ts, value=ts),
            })
            ts += 1

    def reader() -> None:
        while not stop.is_set():
            storage = make_storage()
            records = storage.get_changed_since('sync_tests.SyncTestModel', 99)
            counts.append(len(records))
            errors.extend(
                AssertionError(f'stale record: {rec}')
                for rec in records.values()
                if rec.sync_field_last_modified <= 99
            )

    threads = (
        [threading.Thread(target=thread_safe(writer, errors)) for _ in range(2)]
        + [threading.Thread(target=thread_safe(reader, errors)) for _ in range(3)]
    )

    for t in threads:
        t.start()

    time.sleep(2.0)
    stop.set()

    for t in threads:
        t.join(timeout=10)

    assert not errors, f'errors: {errors[:3]}'
    assert all(c == 50 for c in counts), f'count drifted: {sorted(set(counts))}'


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_concurrent_m2m_assignment_consistent() -> None:
    tag_a = SyncTestTag.objects.create(label='alpha')
    tag_b = SyncTestTag.objects.create(label='beta')
    tag_c = SyncTestTag.objects.create(label='gamma')

    key = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'

    setup = make_storage()
    setup.upsert_many('sync_tests.SyncTestModel', {
        key: SyncRecord(
            key=key,
            data={'id': key, 'name': 'host', 'value': 0, 'tags': []},
            timestamps={'name': 100, 'value': 100, 'tags': 100},
        ),
    })

    barrier = threading.Barrier(3)
    errors: list[Exception] = []

    def assign(tag_pks: list[str], ts: int) -> None:
        storage = make_storage()
        storage.upsert_many('sync_tests.SyncTestModel', {
            key: SyncRecord(
                key=key,
                data={
                    'id': key,
                    'name': 'host',
                    'value': 0,
                    'tags': tag_pks,
                },
                timestamps={'name': 100, 'value': 100, 'tags': ts},
            ),
        })

    threads = [
        threading.Thread(
            target=thread_safe(assign, errors, barrier=barrier),
            args=([str(tag_a.pk)], 200),
        ),
        threading.Thread(
            target=thread_safe(assign, errors, barrier=barrier),
            args=([str(tag_b.pk)], 300),
        ),
        threading.Thread(
            target=thread_safe(assign, errors, barrier=barrier),
            args=([str(tag_a.pk), str(tag_c.pk)], 400),
        ),
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=10)

    assert not errors, f'errors: {errors}'

    obj = SyncTestModel.objects.get(pk=key)
    final_tags = set(obj.tags.values_list('pk', flat=True))

    assert final_tags in (
        {tag_a.pk},
        {tag_b.pk},
        {tag_a.pk, tag_c.pk},
    ), f'unexpected M2M state: {final_tags}'
    assert obj.sync_field_timestamps.get('tags', 0) >= 200


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_reader_during_concurrent_writers_no_lost_updates() -> None:
    setup = make_storage()
    seed_records = {}

    for i in range(20):
        k = f'{i:08d}-0000-0000-0000-aaaaaaaaaaaa'
        seed_records[k] = make_named_record(k, f'seed-{i}', 100, value=i)

    setup.upsert_many('sync_tests.SyncTestModel', seed_records)

    stop = threading.Event()
    errors: list[Exception] = []

    def writer(wid: int) -> None:
        ts = 500 + wid * 100_000
        while not stop.is_set():
            storage = make_storage()
            k = f'{ts % 20:08d}-0000-0000-0000-aaaaaaaaaaaa'
            storage.upsert_many('sync_tests.SyncTestModel', {
                k: make_named_record(k, f'w{wid}-{ts}', ts, value=ts),
            })
            ts += 1

    def reader() -> None:
        keys = {f'{i:08d}-0000-0000-0000-aaaaaaaaaaaa' for i in range(20)}
        while not stop.is_set():
            storage = make_storage()
            records = storage.get_records('sync_tests.SyncTestModel', keys)
            if len(records) != 20:
                errors.append(AssertionError(f'partial read: {len(records)} records'))

    threads = (
        [
            threading.Thread(
                target=thread_safe(writer, errors),
                args=(w,),
            )
            for w in range(3)
        ]
        + [threading.Thread(target=thread_safe(reader, errors)) for _ in range(3)]
    )

    for t in threads:
        t.start()

    time.sleep(2.0)
    stop.set()

    for t in threads:
        t.join(timeout=10)

    assert not errors, f'errors: {errors[:3]}'
    assert SyncTestModel.objects.count() == 20
