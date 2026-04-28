from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.contrib.sync.core.enums import SyncPhase, SyncStatus
    from django_spire.contrib.sync.database.manifest import DatabaseResult


class SyncLock(Protocol):
    def acquire(self, node_id: str) -> str: ...
    def release(self, session_id: str, status: SyncStatus, result: DatabaseResult | None = None) -> None: ...
    def update_phase(self, session_id: str, phase: SyncPhase) -> None: ...
