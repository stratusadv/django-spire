from django.db import models


class SyncTombstone(models.Model):
    model_label = models.CharField(max_length=255)
    record_key = models.CharField(max_length=255)
    timestamp = models.BigIntegerField()
    sequence = models.BigIntegerField(default=0, db_index=True)
    origin_node = models.CharField(max_length=255, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'sync'
        db_table = 'django_spire_sync_tombstone'
        unique_together = [('model_label', 'record_key')]
        indexes = [
            models.Index(
                fields=['model_label', 'sequence'],
                name='sync_tombstone_model_seq_idx',
            ),
            models.Index(
                fields=['model_label', 'timestamp'],
                name='sync_tombstone_model_ts_idx',
            ),
        ]

    def __str__(self) -> str:
        return (
            f'{self.model_label}:{self.record_key} '
            f'seq={self.sequence} ts={self.timestamp}'
        )
