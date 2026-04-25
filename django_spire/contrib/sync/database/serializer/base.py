from __future__ import annotations

from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.contrib.sync.database.record import SyncRecord


class Serializer(Protocol):
    def deserialize(
        self,
        model_label: str,
        record: SyncRecord,
    ) -> Any: ...

    def get_identity(self, instance: Any) -> str: ...

    def serialize(self, instance: Any) -> SyncRecord: ...
