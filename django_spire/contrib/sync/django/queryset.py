from __future__ import annotations

import threading

from contextlib import contextmanager
from typing import Any, Iterator

from django.db import models


_bypass = threading.local()


def _is_bypassed() -> bool:
    return getattr(_bypass, 'active', False)


@contextmanager
def sync_bypass() -> Iterator[None]:
    previous = getattr(_bypass, 'active', False)
    _bypass.active = True

    try:
        yield
    finally:
        _bypass.active = previous


class SyncableQuerySet(models.QuerySet):
    def bulk_create(
        self,
        objs: list[Any],
        **kwargs: Any,
    ) -> list[Any]:
        if _is_bypassed():
            return super().bulk_create(objs, **kwargs)

        if not objs:
            return super().bulk_create(objs, **kwargs)

        clock = self.model.get_clock()

        for instance in objs:
            if not hasattr(instance, 'get_syncable_field_names'):
                continue

            now = clock.now()
            timestamps = dict(instance.sync_field_timestamps)

            for name in instance.get_syncable_field_names():
                if name not in timestamps:
                    timestamps[name] = now

            instance.sync_field_timestamps = timestamps

            if not instance.sync_field_last_modified:
                instance.sync_field_last_modified = now

        return super().bulk_create(objs, **kwargs)

    def bulk_update(
        self,
        objs: list[Any],
        fields: list[str] | tuple[str, ...],
        **kwargs: Any,
    ) -> int:
        if _is_bypassed():
            return super().bulk_update(objs, fields, **kwargs)

        if not objs:
            return super().bulk_update(objs, fields, **kwargs)

        clock = self.model.get_clock()
        needs_extra = False

        for instance in objs:
            if not hasattr(instance, '_sync_exclude_fields'):
                continue

            syncable = set(instance.get_syncable_field_names())
            dirty = syncable & set(fields)

            if not dirty:
                continue

            now = clock.now()
            timestamps = dict(instance.sync_field_timestamps)

            for name in dirty:
                timestamps[name] = now

            instance.sync_field_timestamps = timestamps
            instance.sync_field_last_modified = now
            needs_extra = True

        if needs_extra:
            sync_fields = {
                'sync_field_timestamps',
                'sync_field_last_modified',
            }

            fields = list(set(fields) | sync_fields)

        return super().bulk_update(objs, fields, **kwargs)
