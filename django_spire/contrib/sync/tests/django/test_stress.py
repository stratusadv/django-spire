from __future__ import annotations

import threading
import time

import pytest

from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.database.engine import DatabaseEngine
from django_spire.contrib.sync.database.graph import DependencyGraph
from django_spire.contrib.sync.database.manifest import ModelPayload
from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.tests.django.helpers import (
    make_named_record,
    make_storage,
    thread_safe,
    uuid_from_ints,
)
from django_spire.contrib.sync.tests.factories import make_manifest
from django_spire.contrib.sync.tests.models import SyncTestModel


pytestmark = pytest.mark.slow


@pytest.mark.django_db(transaction=True)
def test_upsert_5000_records_single_batch() -> None:
    storage = make_storage()

    records = {}

    for i in range(5_000):
        key = uuid_from_ints(0, i)
        records[key] = make_named_record(key, f'record-{i}', 100, value=i)

    start = time.monotonic()
    skipped = storage.upsert_many('sync_tests.SyncTestModel', records)
    elapsed = time.monotonic() - start

    assert len(skipped) == 0

    count = SyncTestModel.objects.filter(pk__in=list(records.keys())).count()

    assert count == 5_000
    assert elapsed < 60.0, f'5k single-batch upsert took {elapsed:.2f}s'


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_ten_writers_500_keys_each_no_loss() -> None:
    num_workers = 10
    keys_per_worker = 500
    barrier = threading.Barrier(num_workers)

    errors: list[Exception] = []

    all_keys: list[str] = []

    all_keys: list[str] = [
        uuid_from_ints(w + 1, i)
        for w in range(num_workers)
        for i in range(keys_per_worker)
    ]

    def batch_upsert(worker_id: int) -> None:
        storage = make_storage()

        records = {}

        for i in range(keys_per_worker):
            key = uuid_from_ints(worker_id + 1, i)
            records[key] = make_named_record(key, f'w{worker_id}-r{i}', 200, value=i)

        storage.upsert_many('sync_tests.SyncTestModel', records)

    threads = [
        threading.Thread(
            target=thread_safe(batch_upsert, errors, barrier=barrier, barrier_timeout=10.0),
            args=(w,),
        )
        for w in range(num_workers)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=120)

    assert not errors, f'errors: {errors[:3]}'

    existing = {
        str(pk)
        for pk in SyncTestModel.objects.filter(pk__in=all_keys).values_list('pk', flat=True)
    }

    assert existing == set(all_keys)


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_twenty_writers_single_key_highest_ts_wins() -> None:
    key = uuid_from_ints(0xDEAD, 0xBEEF)
    num_workers = 20
    barrier = threading.Barrier(num_workers)

    errors: list[Exception] = []

    def upsert_one(worker_id: int) -> None:
        storage = make_storage()
        storage.upsert_many('sync_tests.SyncTestModel', {
            key: make_named_record(key, f'writer-{worker_id}', 100 + worker_id, value=worker_id),
        })

    threads = [
        threading.Thread(
            target=thread_safe(upsert_one, errors, barrier=barrier, barrier_timeout=10.0),
            args=(w,),
        )
        for w in range(num_workers)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=30)

    assert not errors, f'errors: {errors}'

    objs = SyncTestModel.objects.filter(pk=key)

    assert objs.count() == 1

    obj = objs.get()

    assert obj.sync_field_last_modified == 100 + (num_workers - 1)
    assert obj.name == f'writer-{num_workers - 1}'


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_concurrent_process_interleaved_creates() -> None:
    barrier = threading.Barrier(3)
    errors: list[Exception] = []

    tablet_keys: dict[str, list[str]] = {}

    for prefix_idx, tablet_id in enumerate(['tablet-1', 'tablet-2', 'tablet-3']):
        tablet_keys[tablet_id] = [
            uuid_from_ints(prefix_idx + 0xAA, i) for i in range(20)
        ]

    def process_creates(tablet_id: str) -> None:
        storage = make_storage()
        models = storage.get_syncable_models()
        graph = DependencyGraph({m: set() for m in models})

        engine = DatabaseEngine(
            storage=storage,
            graph=graph,
            clock=HybridLogicalClock(),
            node_id='server',
            clock_drift_max=None,
        )

        records = {}

        for i, key in enumerate(tablet_keys[tablet_id]):
            records[key] = SyncRecord(
                key=key,
                data={'id': key, 'name': f'{tablet_id}-r{i}', 'value': i},
                timestamps={'name': 200, 'value': 200},
            )

        manifest = make_manifest(
            node_id=tablet_id,
            checkpoint=0,
            node_time=int(time.time()),
            payloads=[
                ModelPayload(
                    model_label='sync_tests.SyncTestModel',
                    records=records,
                ),
            ],
        )

        engine.process(manifest)

    threads = [
        threading.Thread(
            target=thread_safe(process_creates, errors, barrier=barrier),
            args=(tablet_id,),
        )
        for tablet_id in tablet_keys
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=30)

    assert not errors, f'errors: {errors}'

    all_keys: list[str] = []

    for keys in tablet_keys.values():
        all_keys.extend(keys)

    persisted = SyncTestModel.objects.filter(pk__in=all_keys).count()

    assert persisted == 60


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_sustained_throughput_floor() -> None:
    duration = 5.0
    num_workers = 8
    barrier = threading.Barrier(num_workers)
    stop = threading.Event()

    counters: list[int] = [0] * num_workers
    errors: list[Exception] = []

    def worker(wid: int) -> None:
        storage = make_storage()
        ts = 1
        while not stop.is_set():
            key = uuid_from_ints(wid + 1, counters[wid])
            storage.upsert_many('sync_tests.SyncTestModel', {
                key: make_named_record(key, f'w{wid}', ts, value=counters[wid]),
            })
            counters[wid] += 1
            ts += 1

    threads = [
        threading.Thread(
            target=thread_safe(worker, errors, barrier=barrier, barrier_timeout=10.0),
            args=(w,),
        )
        for w in range(num_workers)
    ]

    start = time.monotonic()

    for t in threads:
        t.start()

    time.sleep(duration)
    stop.set()

    for t in threads:
        t.join(timeout=30)

    elapsed = time.monotonic() - start

    assert not errors, f'errors: {errors[:3]}'

    total = sum(counters)
    throughput = total / elapsed

    assert throughput >= 50.0, (
        f'throughput {throughput:.1f} ops/s under floor (total={total}, elapsed={elapsed:.2f}s)'
    )

    assert SyncTestModel.objects.count() == total


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_get_changed_since_returns_all_records_under_load() -> None:
    storage = make_storage(batch_size_max=10_000)

    records = {}

    for i in range(10_000):
        key = uuid_from_ints(0xCAFE, i)
        records[key] = make_named_record(key, f'r{i}', 100, value=i)

    storage.upsert_many('sync_tests.SyncTestModel', records)

    start = time.monotonic()
    fetched = storage.get_changed_since('sync_tests.SyncTestModel', 50)
    elapsed = time.monotonic() - start

    assert len(fetched) == 10_000
    assert elapsed < 30.0, f'get_changed_since took {elapsed:.2f}s for 10k records'


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_mixed_read_write_load() -> None:
    setup = make_storage()
    seed_records = {}

    for i in range(100):
        key = uuid_from_ints(0xBEEF, i)
        seed_records[key] = make_named_record(key, f'seed-{i}', 100, value=i)

    setup.upsert_many('sync_tests.SyncTestModel', seed_records)

    duration = 3.0
    stop = threading.Event()
    errors: list[Exception] = []
    read_counts: list[int] = []
    write_counts: list[int] = [0, 0, 0, 0]

    def writer(wid: int) -> None:
        storage = make_storage()
        ts = 200 + wid * 100_000
        while not stop.is_set():
            key = uuid_from_ints(0xBEEF, write_counts[wid] % 100)
            storage.upsert_many('sync_tests.SyncTestModel', {
                key: make_named_record(key, f'w{wid}', ts, value=write_counts[wid]),
            })
            write_counts[wid] += 1
            ts += 1

    def reader() -> None:
        storage = make_storage()
        local = 0
        while not stop.is_set():
            fetched = storage.get_records(
                'sync_tests.SyncTestModel',
                {uuid_from_ints(0xBEEF, i) for i in range(0, 100, 5)},
            )
            local += len(fetched)
        read_counts.append(local)

    threads = (
        [
            threading.Thread(target=thread_safe(writer, errors), args=(w,))
            for w in range(4)
        ]
        + [threading.Thread(target=thread_safe(reader, errors)) for _ in range(4)]
    )

    for t in threads:
        t.start()

    time.sleep(duration)
    stop.set()

    for t in threads:
        t.join(timeout=30)

    assert not errors, f'errors: {errors[:3]}'
    assert sum(write_counts) > 0
    assert sum(read_counts) > 0
    assert SyncTestModel.objects.count() == 100
