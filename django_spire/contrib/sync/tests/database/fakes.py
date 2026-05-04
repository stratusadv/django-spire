from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.contrib.sync.core.enums import SyncPhase, SyncStatus


class FakeLock:
    def __init__(self) -> None:
        self.acquired: list[str] = []
        self.released: list[tuple[str, SyncStatus]] = []
        self.phases: list[tuple[str, SyncPhase]] = []

    def acquire(self, node_id: str) -> str:
        session_id = f'session-{len(self.acquired)}'
        self.acquired.append(node_id)
        return session_id

    def release(
        self,
        session_id: str,
        status: SyncStatus,
        result: Any = None,
    ) -> None:
        _ = result

        self.released.append((session_id, status))

    def update_phase(self, session_id: str, phase: SyncPhase) -> None:
        self.phases.append((session_id, phase))
