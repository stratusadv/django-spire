from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from django_spire.contrib.sync.core.hash import RecordHasher


class FileSyncableQuerySet(QuerySet):
    def _compute_hashes(self, objs: list[Any]) -> None:
        if not objs:
            return

        model = self.model
        identity_field = getattr(model, '_file_sync_identity_field', '')
        sync_fields = getattr(model, '_file_sync_fields', ())

        if not identity_field or not sync_fields:
            return

        get_hasher = getattr(model, '_get_hasher', None)

        hasher = (
            get_hasher()
            if get_hasher is not None
            else RecordHasher(identity_field)
        )

        for instance in objs:
            record = {
                field: getattr(instance, field)
                for field in sync_fields
            }

            instance.sync_field_hash = hasher.hash(record)

    def bulk_create(self, objs: list[Any], **kwargs: Any) -> list[Any]:
        self._compute_hashes(objs)
        return super().bulk_create(objs, **kwargs)

    def bulk_update(self, objs: list[Any], fields: list[str] | tuple[str, ...], **kwargs: Any) -> int:
        self._compute_hashes(objs)

        field_set = set(fields)
        field_set.add('sync_field_hash')

        return super().bulk_update(objs, list(field_set), **kwargs)
