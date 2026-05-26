from django.db import models


class SyncDeferredBackfill(models.Model):
    model_label = models.CharField(max_length=255)
    record_key = models.CharField(max_length=255)
    attname = models.CharField(max_length=255)
    fk_value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'sync'
        db_table = 'django_spire_sync_deferred_backfill'
        unique_together = [('model_label', 'record_key', 'attname')]
        indexes = [
            models.Index(
                fields=['model_label'],
                name='sync_deferred_bf_idx',
            ),
        ]

    def __str__(self) -> str:
        return (
            f'{self.model_label}:{self.record_key} '
            f'{self.attname}={self.fk_value}'
        )
