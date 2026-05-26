from django.db import models


class SyncNodeLock(models.Model):
    node_id = models.CharField(max_length=255)
    peer_node_id = models.CharField(max_length=255, default='', blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'sync'
        db_table = 'django_spire_sync_node_lock'
        unique_together = [('node_id', 'peer_node_id')]

    def __str__(self) -> str:
        return f'lock:{self.node_id}<->{self.peer_node_id}'
