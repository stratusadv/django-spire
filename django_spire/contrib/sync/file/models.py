from __future__ import annotations

from typing import Any, ClassVar

from django.db import models

from django_spire.contrib.sync.core.hash import RecordHasher


class FileSyncableMixin(models.Model):
    SYNC_HASH_FIELD = 'sync_field_hash'

    sync_field_hash = models.CharField(max_length=128, default='', blank=True, editable=False)

    _file_sync_identity_field: ClassVar[str] = ''
    _file_sync_fields: ClassVar[tuple[str, ...]] = ()

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self._file_sync_fields:
            self.sync_field_hash = self._compute_sync_hash()

        super().save(*args, **kwargs)

    @classmethod
    def _get_hasher(cls) -> RecordHasher:
        hasher = cls.__dict__.get('_file_sync_hasher')

        if hasher is None:
            hasher = RecordHasher(cls._file_sync_identity_field)
            cls._file_sync_hasher = hasher

        return hasher

    def _compute_sync_hash(self) -> str:
        if not self._file_sync_fields or not self._file_sync_identity_field:
            return ''

        record = {
            field: getattr(self, field)
            for field in self._file_sync_fields
        }

        return self._get_hasher().hash(record)
