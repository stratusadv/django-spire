from __future__ import annotations

from typing import Any

from django_spire.contrib.sync.django.models.checkpoint import SyncCheckpoint


class DjangoCheckpointStore:
    def get_after_keys(self, peer_node_id: str) -> dict[str, Any]:
        checkpoint = (
            SyncCheckpoint.objects
            .filter(peer_node_id=peer_node_id)
            .first()
        )

        if checkpoint is None:
            return {}

        return checkpoint.after_keys or {}

    def get_checkpoint(self, peer_node_id: str) -> tuple[int, int]:
        checkpoint = (
            SyncCheckpoint.objects
            .filter(peer_node_id=peer_node_id)
            .first()
        )

        if checkpoint is None:
            return 0, 0

        return checkpoint.peer_sequence, checkpoint.local_sequence_pushed

    def save_checkpoint(
        self,
        peer_node_id: str,
        peer_sequence: int,
        local_sequence_pushed: int,
        after_keys: dict[str, Any] | None = None,
    ) -> None:
        SyncCheckpoint.objects.update_or_create(
            peer_node_id=peer_node_id,
            defaults={
                'after_keys': after_keys or {},
                'local_sequence_pushed': local_sequence_pushed,
                'peer_sequence': peer_sequence,
            },
        )
