from __future__ import annotations

import threading
import time

import pytest

from django_spire.contrib.sync.core.enums import SyncStatus
from django_spire.contrib.sync.core.exceptions import LockContentionError
from django_spire.contrib.sync.django.lock import DjangoSyncLock
from django_spire.contrib.sync.django.models.session import SyncSession
from django_spire.contrib.sync.tests.django.helpers import thread_safe


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_lock_five_threads_one_winner() -> None:
    lock = DjangoSyncLock()
    barrier = threading.Barrier(5)

    successes: list[str] = []
    contentions: list[BaseException] = []
    errors: list[Exception] = []

    def try_acquire() -> None:
        session_id = lock.acquire('contention-node')
        successes.append(session_id)
        time.sleep(0.02)

    threads = [
        threading.Thread(
            target=thread_safe(
                try_acquire,
                errors,
                barrier=barrier,
                on_caught={LockContentionError: contentions},
            ),
        )
        for _ in range(5)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=10)

    assert not errors, f'errors: {errors}'
    assert len(successes) == 1
    assert len(contentions) == 4


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_lock_rapid_acquire_release_cycling() -> None:
    lock = DjangoSyncLock()
    errors: list[Exception] = []

    def cycle(node_id: str, iterations: int) -> None:
        for _ in range(iterations):
            session_id = lock.acquire(node_id)
            lock.release(session_id, SyncStatus.SUCCESS)

    threads = [
        threading.Thread(
            target=thread_safe(cycle, errors),
            args=(f'cycle-node-{i}', 10),
        )
        for i in range(3)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=30)

    assert not errors, f'errors: {errors}'

    active = SyncSession.objects.filter(status=SyncStatus.IN_PROGRESS).count()

    assert active == 0


@pytest.mark.postgres_only
@pytest.mark.django_db(transaction=True)
def test_lock_release_then_two_competitors_only_one_wins() -> None:
    lock = DjangoSyncLock()
    initial = lock.acquire('race-node')
    lock.release(initial, SyncStatus.SUCCESS)

    barrier = threading.Barrier(2)
    successes: list[str] = []
    contentions: list[BaseException] = []
    errors: list[Exception] = []

    def acquire_worker() -> None:
        session_id = lock.acquire('race-node')
        successes.append(session_id)

    threads = [
        threading.Thread(
            target=thread_safe(
                acquire_worker,
                errors,
                barrier=barrier,
                on_caught={LockContentionError: contentions},
            ),
        )
        for _ in range(2)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=10)

    assert not errors, f'errors: {errors}'
    assert len(successes) == 1
    assert len(contentions) == 1

    active = SyncSession.objects.filter(
        node_id='race-node',
        status=SyncStatus.IN_PROGRESS,
    ).count()

    assert active == 1
