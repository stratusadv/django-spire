import uuid

from django.db import models


class SyncSession(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    node_id = models.CharField(max_length=255)
    phase = models.CharField(max_length=20, default='collecting')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')

    records_pushed = models.PositiveIntegerField(default=0)
    records_applied = models.PositiveIntegerField(default=0)
    records_created = models.PositiveIntegerField(default=0)
    records_deleted = models.PositiveIntegerField(default=0)
    conflicts = models.PositiveIntegerField(default=0)
    errors = models.PositiveIntegerField(default=0)

    details = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'sync'
        indexes = [
            models.Index(
                fields=['node_id', 'status'],
                name='sync_session_node_status_idx',
            ),
        ]
        ordering = ['-started_at']

    def __str__(self) -> str:
        return f'{self.node_id} [{self.status}] {self.started_at}'
