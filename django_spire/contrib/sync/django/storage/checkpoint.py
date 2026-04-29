from __future__ import annotations

from django_spire.contrib.sync.django.models.checkpoint import SyncCheckpoint


class DjangoCheckpointStore:
    def get_checkpoint(self, node_id: str) -> int:
        checkpoint = (
            SyncCheckpoint.objects
            .filter(node_id=node_id)
            .first()
        )

        if checkpoint is None:
            return 0

        return checkpoint.timestamp

    def save_checkpoint(self, node_id: str, timestamp: int) -> None:
        SyncCheckpoint.objects.update_or_create(
            node_id=node_id,
            defaults={'timestamp': timestamp},
        )
