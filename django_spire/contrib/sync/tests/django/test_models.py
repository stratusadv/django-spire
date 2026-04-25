from __future__ import annotations

from datetime import timedelta

import pytest

from django.db import IntegrityError
from django.utils import timezone

from django_spire.contrib.sync.core.enums import SyncPhase, SyncStatus
from django_spire.contrib.sync.django.models.checkpoint import SyncCheckpoint
from django_spire.contrib.sync.django.models.lock import SyncNodeLock
from django_spire.contrib.sync.django.models.session import SyncSession


@pytest.mark.django_db
def test_sync_checkpoint_node_id_is_unique() -> None:
    SyncCheckpoint.objects.create(node_id='node-1', timestamp=100)

    with pytest.raises(IntegrityError):
        SyncCheckpoint.objects.create(node_id='node-1', timestamp=200)


@pytest.mark.django_db
def test_sync_checkpoint_default_timestamp_is_zero() -> None:
    cp = SyncCheckpoint.objects.create(node_id='node-1')

    assert cp.timestamp == 0


@pytest.mark.django_db
def test_sync_node_lock_node_id_is_unique() -> None:
    SyncNodeLock.objects.create(node_id='node-1')

    with pytest.raises(IntegrityError):
        SyncNodeLock.objects.create(node_id='node-1')


@pytest.mark.django_db
def test_sync_session_default_status_is_pending() -> None:
    session = SyncSession.objects.create(node_id='node-1')

    assert session.status == SyncStatus.PENDING
    assert session.completed_at is None


@pytest.mark.django_db
def test_sync_session_started_at_is_auto_set() -> None:
    before = timezone.now()
    session = SyncSession.objects.create(node_id='node-1')
    after = timezone.now()

    assert before - timedelta(seconds=1) <= session.started_at <= after + timedelta(seconds=1)


@pytest.mark.django_db
def test_sync_session_filter_by_in_progress_excludes_terminal_states() -> None:
    SyncSession.objects.create(
        node_id='node-1',
        status=SyncStatus.SUCCESS,
        completed_at=timezone.now(),
    )
    SyncSession.objects.create(
        node_id='node-1',
        status=SyncStatus.FAILURE,
        completed_at=timezone.now(),
    )
    SyncSession.objects.create(
        node_id='node-1',
        status=SyncStatus.PENDING,
    )
    active = SyncSession.objects.create(
        node_id='node-1',
        status=SyncStatus.IN_PROGRESS,
        phase=SyncPhase.COLLECTING,
    )

    found = list(SyncSession.objects.filter(
        node_id='node-1',
        status=SyncStatus.IN_PROGRESS,
    ))

    assert found == [active]


@pytest.mark.django_db
def test_sync_session_id_is_uuid() -> None:
    session = SyncSession.objects.create(node_id='node-1')

    assert len(str(session.id)) == 36
    assert str(session.id).count('-') == 4
