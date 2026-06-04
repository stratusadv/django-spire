from __future__ import annotations

from typing import Any

from django_spire.sync.database.storage import CheckpointPosition
from django_spire.sync.django.models.checkpoint import SyncCheckpoint


class DjangoCheckpointStore:
    def get_after_keys(self, peer_node_id: str) -> dict[str, Any]:
        checkpoint = SyncCheckpoint.objects.filter(peer_node_id=peer_node_id).first()

        if checkpoint is None:
            return {}

        return checkpoint.after_keys or {}

    def get_checkpoint(self, peer_node_id: str) -> CheckpointPosition:
        checkpoint = SyncCheckpoint.objects.filter(peer_node_id=peer_node_id).first()

        if checkpoint is None:
            return CheckpointPosition(peer_sequence=0, local_sequence_pushed=0)

        return CheckpointPosition(
            peer_sequence=checkpoint.peer_sequence,
            local_sequence_pushed=checkpoint.local_sequence_pushed,
        )

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
