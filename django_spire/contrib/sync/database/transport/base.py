from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.contrib.sync.database.manifest import SyncManifest


class Transport(Protocol):
    def exchange(self, manifest: SyncManifest) -> SyncManifest: ...
