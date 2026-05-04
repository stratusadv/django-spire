from django.db import models


class SyncCheckpoint(models.Model):
    after_keys = models.JSONField(default=dict, blank=True)
    node_id = models.CharField(max_length=255, unique=True)
    timestamp = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'sync'
        db_table = 'django_spire_sync_checkpoint'

    def __str__(self) -> str:
        return f'{self.node_id} @ {self.timestamp}'
