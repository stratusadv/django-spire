from django.db import models


class SyncSequenceCounter(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    value = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'sync'
        db_table = 'django_spire_sync_sequence_counter'

    def __str__(self) -> str:
        return f'{self.name} @ {self.value}'
