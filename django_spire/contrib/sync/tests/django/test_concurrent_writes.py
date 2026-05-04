from __future__ import annotations

import threading
import time

from typing import Any

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
)
from django_spire.contrib.sync.tests.factories import make_manifest
from django_spire.contrib.sync.tests.models import SyncTestModel


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_concurrent_upsert_same_key_no_data_loss() -> None:
    key = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    barrier = threading.Barrier(4)

    errors: list[Exception] = []

    def upsert_worker(name: str, ts: int) -> None:
        storage = make_storage()
        storage.upsert_many('sync_tests.SyncTestModel', {
            key: make_named_record(key, name, ts),
        })

    threads = [
        threading.Thread(
            target=thread_safe(upsert_worker, errors, barrier=barrier),
            args=(f'writer-{i}', 100 + i),
        )
        for i in range(4)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=10)

    assert not errors, f'worker errors: {errors}'

    objs = SyncTestModel.objects.filter(pk=key)

    assert objs.count() == 1

    obj = objs.get()

    assert obj.sync_field_last_modified == 103
    assert obj.name == 'writer-3'
    assert obj.sync_field_timestamps == {'name': 103, 'value': 103}


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_concurrent_upsert_highest_timestamp_wins() -> None:
    key = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    barrier = threading.Barrier(2)

    errors: list[Exception] = []

    def upsert_worker(name: str, ts: int) -> None:
        storage = make_storage()
        storage.upsert_many('sync_tests.SyncTestModel', {
            key: make_named_record(key, name, ts),
        })

    t1 = threading.Thread(
        target=thread_safe(upsert_worker, errors, barrier=barrier),
        args=('low', 100),
    )
    t2 = threading.Thread(
        target=thread_safe(upsert_worker, errors, barrier=barrier),
        args=('high', 999),
    )

    t1.start()
    t2.start()
    t1.join(timeout=10)
    t2.join(timeout=10)

    assert not errors, f'worker errors: {errors}'

    obj = SyncTestModel.objects.get(pk=key)

    assert obj.sync_field_last_modified == 999
    assert obj.name == 'high'
    assert obj.sync_field_timestamps == {'name': 999, 'value': 999}


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_concurrent_upsert_many_keys_no_missing_records() -> None:
    num_workers = 4
    keys_per_worker = 10
    barrier = threading.Barrier(num_workers)

    errors: list[Exception] = []
    all_keys: list[str] = []

    def upsert_batch(worker_id: int) -> None:
        storage = make_storage()

        records = {}

        for i in range(keys_per_worker):
            key = f'{worker_id:08d}-0000-0000-0000-{i:012d}'
            records[key] = make_named_record(key, f'w{worker_id}-r{i}', 200)

        storage.upsert_many('sync_tests.SyncTestModel', records)

    all_keys: list[str] = [
        f'{w:08d}-0000-0000-0000-{i:012d}'
        for w in range(num_workers)
        for i in range(keys_per_worker)
    ]

    threads = [
        threading.Thread(
            target=thread_safe(upsert_batch, errors, barrier=barrier),
            args=(w,),
        )
        for w in range(num_workers)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=15)

    assert not errors, f'worker errors: {errors}'

    existing = {
        str(pk)
        for pk in SyncTestModel.objects.filter(
            pk__in=all_keys,
        ).values_list('pk', flat=True)
    }

    assert existing == set(all_keys)


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_concurrent_soft_delete_and_upsert() -> None:
    key = 'cccccccc-cccc-cccc-cccc-cccccccccccc'

    setup_storage = make_storage()
    setup_storage.upsert_many('sync_tests.SyncTestModel', {
        key: make_named_record(key, 'original', 100),
    })

    barrier = threading.Barrier(2)
    errors: list[Exception] = []

    def do_delete() -> None:
        storage = make_storage()
        storage.delete_many('sync_tests.SyncTestModel', {key: 500})

    def do_upsert() -> None:
        storage = make_storage()
        storage.upsert_many('sync_tests.SyncTestModel', {
            key: make_named_record(key, 'updated', 600, value=99),
        })

    t1 = threading.Thread(target=thread_safe(do_delete, errors, barrier=barrier))
    t2 = threading.Thread(target=thread_safe(do_upsert, errors, barrier=barrier))

    t1.start()
    t2.start()
    t1.join(timeout=10)
    t2.join(timeout=10)

    assert not errors, f'errors: {errors}'

    obj = SyncTestModel.objects.get(pk=key)

    assert obj.sync_field_last_modified == 600
    assert obj.name == 'updated'


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_concurrent_process_calls_no_data_loss() -> None:
    barrier = threading.Barrier(2)
    results: list[Any] = []
    errors: list[Exception] = []

    def process_tablet(node_id: str, key: str, name: str, ts: int) -> None:
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

        manifest = make_manifest(
            node_id=node_id,
            checkpoint=0,
            node_time=int(time.time()),
            payloads=[
                ModelPayload(
                    model_label='sync_tests.SyncTestModel',
                    records={
                        key: SyncRecord(
                            key=key,
                            data={'id': key, 'name': name, 'value': 0},
                            timestamps={'name': ts, 'value': ts},
                        ),
                    },
                ),
            ],
        )

        _response, result = engine.process(manifest)
        results.append(result)

    key_a = 'dddddddd-dddd-dddd-dddd-dddddddddddd'
    key_b = 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'

    t1 = threading.Thread(
        target=thread_safe(process_tablet, errors, barrier=barrier),
        args=('tablet-1', key_a, 'from-t1', 300),
    )
    t2 = threading.Thread(
        target=thread_safe(process_tablet, errors, barrier=barrier),
        args=('tablet-2', key_b, 'from-t2', 300),
    )

    t1.start()
    t2.start()
    t1.join(timeout=15)
    t2.join(timeout=15)

    assert not errors, f'errors: {errors}'
    assert len(results) == 2

    a = SyncTestModel.objects.get(pk=key_a)
    b = SyncTestModel.objects.get(pk=key_b)

    assert a.name == 'from-t1'
    assert a.value == 0
    assert a.sync_field_last_modified > 300

    assert b.name == 'from-t2'
    assert b.value == 0
    assert b.sync_field_last_modified > 300


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_concurrent_process_same_key_no_duplicate_rows() -> None:
    key = 'ffffffff-ffff-ffff-ffff-ffffffffffff'

    setup_storage = make_storage()
    setup_storage.upsert_many('sync_tests.SyncTestModel', {
        key: make_named_record(key, 'seed', 50),
    })

    barrier = threading.Barrier(2)
    errors: list[Exception] = []

    def process_update(node_id: str, name: str, ts: int) -> None:
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

        manifest = make_manifest(
            node_id=node_id,
            checkpoint=0,
            node_time=int(time.time()),
            payloads=[
                ModelPayload(
                    model_label='sync_tests.SyncTestModel',
                    records={
                        key: SyncRecord(
                            key=key,
                            data={'id': key, 'name': name, 'value': 0},
                            timestamps={'name': ts, 'value': ts},
                        ),
                    },
                ),
            ],
        )

        engine.process(manifest)

    t1 = threading.Thread(
        target=thread_safe(process_update, errors, barrier=barrier),
        args=('tablet-1', 'low', 100),
    )
    t2 = threading.Thread(
        target=thread_safe(process_update, errors, barrier=barrier),
        args=('tablet-2', 'high', 999),
    )

    t1.start()
    t2.start()
    t1.join(timeout=15)
    t2.join(timeout=15)

    assert not errors, f'errors: {errors}'

    objs = SyncTestModel.objects.filter(pk=key)

    assert objs.count() == 1

    obj = objs.get()

    assert obj.name in ('low', 'high', 'seed')
    assert obj.value == 0
    assert obj.sync_field_last_modified > 50
