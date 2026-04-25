from django.db import models


class SyncNodeLock(models.Model):
    node_id = models.CharField(max_length=255, primary_key=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'sync'

    def __str__(self) -> str:
        return f'lock:{self.node_id}'
