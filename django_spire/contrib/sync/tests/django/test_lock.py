from __future__ import annotations

import threading
import time
import uuid

from datetime import timedelta

import pytest

from django.db import connection
from django.utils import timezone

from django_spire.contrib.sync.core.enums import SyncPhase, SyncStatus
from django_spire.contrib.sync.core.exceptions import LockContentionError
from django_spire.contrib.sync.django.lock import DjangoSyncLock
from django_spire.contrib.sync.django.models.session import SyncSession
from django_spire.contrib.sync.tests.django.helpers import thread_safe


@pytest.fixture
def lock() -> DjangoSyncLock:
    return DjangoSyncLock()


@pytest.mark.django_db
def test_acquire_creates_in_progress_session(lock: DjangoSyncLock) -> None:
    session_id = lock.acquire('node-1')

    session = SyncSession.objects.get(id=session_id)

    assert session.status == SyncStatus.IN_PROGRESS
    assert session.node_id == 'node-1'


@pytest.mark.django_db
def test_acquire_rejects_when_active_session_exists(
    lock: DjangoSyncLock,
) -> None:
    lock.acquire('node-1')

    with pytest.raises(LockContentionError, match='already in progress'):
        lock.acquire('node-1')


@pytest.mark.django_db
def test_acquire_allows_after_release(lock: DjangoSyncLock) -> None:
    session_id = lock.acquire('node-1')
    lock.release(session_id, SyncStatus.SUCCESS)

    second = lock.acquire('node-1')

    assert second != session_id


@pytest.mark.django_db
def test_acquire_abandons_stale_session() -> None:
    lock = DjangoSyncLock(timeout_stale=1)

    first_session_id = lock.acquire('node-1')

    SyncSession.objects.filter(id=first_session_id).update(
        started_at=timezone.now() - timedelta(seconds=300),
    )

    second_session_id = lock.acquire('node-1')

    assert second_session_id != first_session_id

    stale = SyncSession.objects.get(id=first_session_id)

    assert stale.status == SyncStatus.ABANDONED


@pytest.mark.django_db
def test_release_records_status(lock: DjangoSyncLock) -> None:
    session_id = lock.acquire('node-1')
    lock.release(session_id, SyncStatus.FAILURE)

    session = SyncSession.objects.get(id=session_id)

    assert session.status == SyncStatus.FAILURE
    assert session.phase == SyncPhase.FAILED
    assert session.completed_at is not None


@pytest.mark.django_db
def test_release_missing_session_does_not_raise(lock: DjangoSyncLock) -> None:
    bogus_id = str(uuid.uuid4())

    lock.release(bogus_id, SyncStatus.SUCCESS)

    assert not SyncSession.objects.filter(id=bogus_id).exists()


@pytest.mark.django_db
def test_update_phase(lock: DjangoSyncLock) -> None:
    session_id = lock.acquire('node-1')

    lock.update_phase(session_id, SyncPhase.RECONCILING)

    session = SyncSession.objects.get(id=session_id)

    assert session.phase == SyncPhase.RECONCILING


@pytest.mark.django_db(transaction=True)
def test_concurrent_acquire_serializes() -> None:
    if connection.vendor == 'sqlite':
        pytest.skip('SQLite does not support concurrent writers for this test')

    lock = DjangoSyncLock()
    successes: list[str] = []
    contentions: list[BaseException] = []
    errors: list[Exception] = []
    barrier = threading.Barrier(2)

    def try_acquire() -> None:
        session_id = lock.acquire('node-concurrent')
        successes.append(session_id)
        time.sleep(0.05)

    threads = [
        threading.Thread(
            target=thread_safe(
                try_acquire,
                errors,
                barrier=barrier,
                on_caught={LockContentionError: contentions},
            ),
        )
        for _ in range(2)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(timeout=10)

    assert not errors, f'errors: {errors}'
    assert len(successes) == 1
    assert len(contentions) == 1
