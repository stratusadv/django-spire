from __future__ import annotations

import threading

from contextlib import contextmanager
from typing import Any, Iterator

from django.db import models, transaction


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

        syncable = [
            instance for instance in objs
            if hasattr(instance, 'get_syncable_field_names')
        ]

        if not syncable:
            return super().bulk_create(objs, **kwargs)

        from django_spire.contrib.sync.django.sequence import (  # noqa: PLC0415
            SyncSequenceAllocator,
        )

        clock = self.model.get_clock()

        with transaction.atomic():
            sequence_first = SyncSequenceAllocator().allocate(len(syncable)).value_first
            sequence_next = sequence_first

            for instance in syncable:
                now = clock.now()
                timestamps = dict(instance.sync_field_timestamps)

                for name in instance.get_syncable_field_names():
                    if name not in timestamps:
                        timestamps[name] = now

                instance.sync_field_timestamps = timestamps

                if not instance.sync_field_last_modified:
                    instance.sync_field_last_modified = now

                if not instance.sync_field_sequence:
                    instance.sync_field_sequence = sequence_next
                    sequence_next += 1

                if not instance.sync_field_origin_node:
                    instance.sync_field_origin_node = ''

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

        syncable = [
            instance for instance in objs
            if hasattr(instance, 'get_syncable_field_names')
        ]

        if not syncable:
            return super().bulk_update(objs, fields, **kwargs)

        from django_spire.contrib.sync.django.sequence import (  # noqa: PLC0415
            SyncSequenceAllocator,
        )

        clock = self.model.get_clock()

        field_set = set(fields)

        stamped_fields = list(field_set | {
            'sync_field_last_modified',
            'sync_field_origin_node',
            'sync_field_sequence',
            'sync_field_timestamps',
        })

        with transaction.atomic():
            sequence_first = SyncSequenceAllocator().allocate(len(syncable)).value_first
            sequence_next = sequence_first

            for instance in syncable:
                now = clock.now()
                timestamps = dict(instance.sync_field_timestamps)

                for name in field_set:
                    if name in instance._sync_exclude_fields:
                        continue

                    timestamps[name] = now

                instance.sync_field_timestamps = timestamps
                instance.sync_field_last_modified = now
                instance.sync_field_sequence = sequence_next
                instance.sync_field_origin_node = ''
                sequence_next += 1

            return super().bulk_update(objs, stamped_fields, **kwargs)

    def update(self, **kwargs: Any) -> int:
        if _is_bypassed():
            return super().update(**kwargs)

        if not hasattr(self.model, 'get_syncable_field_names'):
            return super().update(**kwargs)

        if not kwargs:
            return super().update(**kwargs)

        from django_spire.contrib.sync.django.sequence import (  # noqa: PLC0415
            SyncSequenceAllocator,
        )

        clock = self.model.get_clock()
        exclude = self.model._sync_exclude_fields

        stampable_field_names = [
            name for name in kwargs
            if name not in exclude
        ]

        with transaction.atomic():
            rows = list(
                self.select_for_update().values_list(
                    'pk',
                    'sync_field_timestamps',
                )
            )

            if not rows:
                return 0

            sequence_first = SyncSequenceAllocator().allocate(len(rows)).value_first

            total = 0

            with sync_bypass():
                for index, (primary_key, current_timestamps) in enumerate(rows):
                    now = clock.now()
                    timestamps = dict(current_timestamps or {})

                    for field_name in stampable_field_names:
                        timestamps[field_name] = now

                    update_kwargs = {
                        **kwargs,
                        'sync_field_timestamps': timestamps,
                        'sync_field_last_modified': now,
                        'sync_field_sequence': sequence_first + index,
                        'sync_field_origin_node': '',
                    }

                    total += (
                        self.model.objects
                        .filter(pk=primary_key)
                        .update(**update_kwargs)
                    )

            return total
