from __future__ import annotations

import logging

from datetime import timedelta
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from django_spire.contrib.sync.core.enums import SyncPhase, SyncStatus
from django_spire.contrib.sync.core.exceptions import LockContentionError
from django_spire.contrib.sync.django.models.lock import SyncNodeLock
from django_spire.contrib.sync.django.models.session import SyncSession

if TYPE_CHECKING:
    from django_spire.contrib.sync.database.manifest import DatabaseResult


logger = logging.getLogger(__name__)

_ACTIVE_STATUSES = frozenset({SyncStatus.IN_PROGRESS, SyncStatus.PENDING})
_STALE_TIMEOUT_DEFAULT = 600


class DjangoSyncLock:
    def __init__(
        self,
        timeout_stale: int = _STALE_TIMEOUT_DEFAULT,
    ) -> None:
        self._timeout_stale = timeout_stale

    def _abandon_stale_sessions(self, node_id: str) -> None:
        cutoff = timezone.now() - timedelta(seconds=self._timeout_stale)

        stale = (
            SyncSession.objects
            .filter(
                node_id=node_id,
                started_at__lt=cutoff,
                status__in=_ACTIVE_STATUSES,
            )
        )

        count = stale.update(
            completed_at=timezone.now(),
            phase=SyncPhase.FAILED,
            status=SyncStatus.ABANDONED,
        )

        if count:
            logger.warning(
                'Abandoned %d stale sync session(s) for node %s',
                count,
                node_id,
            )

    def _check_active_session(self, node_id: str) -> None:
        active = (
            SyncSession.objects
            .filter(node_id=node_id, status__in=_ACTIVE_STATUSES)
            .first()
        )

        if active is not None:
            message = (
                f'Sync already in progress for node {node_id!r} '
                f'(session {active.id}, phase={active.phase}). '
                f'Wait for it to complete or let it expire.'
            )

            raise LockContentionError(message)

    def _create_session(self, node_id: str) -> str:
        session = SyncSession.objects.create(
            node_id=node_id,
            phase=SyncPhase.COLLECTING,
            status=SyncStatus.IN_PROGRESS,
        )

        return str(session.id)

    def _ensure_lock_row(self, node_id: str) -> None:
        SyncNodeLock.objects.get_or_create(node_id=node_id)

    def acquire(self, node_id: str) -> str:
        self._ensure_lock_row(node_id)

        with transaction.atomic():
            locked = (
                SyncNodeLock.objects
                .select_for_update()
                .filter(node_id=node_id)
                .first()
            )

            if locked is None:
                message = f'Sync lock row for {node_id!r} is missing after creation'
                raise LockContentionError(message)

            self._abandon_stale_sessions(node_id)
            self._check_active_session(node_id)
            session_id = self._create_session(node_id)

        logger.info(
            'Acquired sync lock for node %s (session %s)',
            node_id,
            session_id,
        )

        return session_id

    def release(
        self,
        session_id: str,
        status: SyncStatus,
        result: DatabaseResult | None = None,
    ) -> None:
        session = (
            SyncSession.objects
            .filter(id=session_id)
            .first()
        )

        if session is None:
            logger.warning(
                'Sync session %s not found during release',
                session_id,
            )

            return

        now = timezone.now()
        elapsed_ms = (now - session.started_at).total_seconds() * 1000

        session.completed_at = now
        session.duration_ms = int(elapsed_ms)

        session.phase = (
            SyncPhase.COMPLETE
            if status == SyncStatus.SUCCESS
            else SyncPhase.FAILED
        )

        session.status = status

        if result is not None:
            session.records_pushed = sum(
                len(keys)
                for keys in result.pushed.values()
            )

            session.records_applied = sum(
                len(keys)
                for keys in result.applied.values()
            )

            session.records_created = sum(
                len(keys)
                for keys in result.created.values()
            )

            session.records_deleted = sum(
                len(keys)
                for keys in result.deleted.values()
            )

            session.conflicts = sum(
                len(keys)
                for keys in result.conflicts.values()
            )

            session.errors = len(result.errors)

        session.save()

        logger.info(
            'Released sync lock for session %s (status=%s)',
            session_id,
            status,
        )

    def update_phase(self, session_id: str, phase: SyncPhase) -> None:
        SyncSession.objects.filter(id=session_id).update(phase=phase)
