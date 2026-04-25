from django.db import models


class SyncCheckpoint(models.Model):
    node_id = models.CharField(max_length=255, unique=True)
    timestamp = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'sync'

    def __str__(self) -> str:
        return f'{self.node_id} @ {self.timestamp}'
