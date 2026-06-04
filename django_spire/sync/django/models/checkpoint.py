from django.db import models


class SyncCheckpoint(models.Model):
    peer_node_id = models.CharField(max_length=255, unique=True)
    peer_sequence = models.BigIntegerField(default=0)
    local_sequence_pushed = models.BigIntegerField(default=0)
    after_keys = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'sync'
        db_table = 'django_spire_sync_checkpoint'

    def __str__(self) -> str:
        return f'{self.peer_node_id} peer={self.peer_sequence} pushed={self.local_sequence_pushed}'
