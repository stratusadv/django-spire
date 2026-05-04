from __future__ import annotations

from typing import Any

from django_spire.contrib.sync.django.models.checkpoint import SyncCheckpoint


class DjangoCheckpointStore:
    def get_after_keys(self, node_id: str) -> dict[str, Any]:
        checkpoint = (
            SyncCheckpoint.objects
            .filter(node_id=node_id)
            .first()
        )

        if checkpoint is None:
            return {}

        return checkpoint.after_keys or {}

    def get_checkpoint(self, node_id: str) -> int:
        checkpoint = (
            SyncCheckpoint.objects
            .filter(node_id=node_id)
            .first()
        )

        if checkpoint is None:
            return 0

        return checkpoint.timestamp

    def save_checkpoint(
        self,
        node_id: str,
        timestamp: int,
        after_keys: dict[str, Any] | None = None,
    ) -> None:
        SyncCheckpoint.objects.update_or_create(
            node_id=node_id,
            defaults={
                'after_keys': after_keys or {},
                'timestamp': timestamp,
            },
        )
