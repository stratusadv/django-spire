from __future__ import annotations

import uuid

from typing import Any, ClassVar, TYPE_CHECKING

from django.db import models

from django_spire.contrib.sync.core.exceptions import ClockNotConfiguredError
from django_spire.contrib.sync.database.tracker import FieldUpdateTracker
from django_spire.contrib.sync.django.queryset import SyncableQuerySet, _is_bypassed

if TYPE_CHECKING:
    from django_spire.contrib.sync.core.clock import HybridLogicalClock


class SyncableMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sync_field_timestamps = models.JSONField(default=dict, editable=False)
    sync_field_last_modified = models.BigIntegerField(default=0, editable=False, db_index=True)

    objects = SyncableQuerySet.as_manager()

    _clock: ClassVar[HybridLogicalClock | None] = None

    _sync_exclude_fields = frozenset({
        'sync_field_timestamps',
        'sync_field_last_modified',
    })

    class Meta:
        abstract = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._tracker = FieldUpdateTracker()
        self._tracker.snapshot(self._get_field_values())

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not _is_bypassed():
            dirty = self.get_dirty_fields()

            if dirty:
                now = self.get_clock().now()
                timestamps = dict(self.sync_field_timestamps)

                for field_name in dirty:
                    timestamps[field_name] = now

                self.sync_field_timestamps = timestamps
                self.sync_field_last_modified = now

        super().save(*args, **kwargs)
        self._tracker.snapshot(self._get_field_values())

    def _get_field_values(self) -> dict[str, Any]:
        return {
            field.name: getattr(self, field.attname)
            for field in self._meta.concrete_fields
            if field.name not in self._sync_exclude_fields
        }

    def get_dirty_fields(self) -> set[str]:
        if self._state.adding:
            return set(self.get_syncable_field_names())

        return self._tracker.get_dirty(self._get_field_values())

    def refresh_from_db(self, *args: Any, **kwargs: Any) -> None:
        super().refresh_from_db(*args, **kwargs)
        self._tracker.snapshot(self._get_field_values())

    @classmethod
    def configure(cls, clock: HybridLogicalClock) -> None:
        cls._clock = clock

    @classmethod
    def get_clock(cls) -> HybridLogicalClock:
        if cls._clock is None:
            message = 'SyncableMixin clock not configured. Call SyncableMixin.configure(clock) in AppConfig.ready().'
            raise ClockNotConfiguredError(message)

        return cls._clock

    @classmethod
    def get_syncable_field_names(cls) -> list[str]:
        return sorted(
            field.name
            for field in cls._meta.concrete_fields
            if field.name not in cls._sync_exclude_fields
        )

    @classmethod
    def get_syncable_m2m_names(cls) -> list[str]:
        return sorted(field.name for field in cls._meta.many_to_many)
