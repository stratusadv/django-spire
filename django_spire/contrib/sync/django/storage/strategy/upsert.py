from __future__ import annotations

import logging
import time

from typing import Any, Protocol, TYPE_CHECKING

from django.db import IntegrityError, transaction

from django_spire.contrib.sync.django.queryset import sync_bypass

if TYPE_CHECKING:
    from django_spire.contrib.sync.database.record import SyncRecord
    from django_spire.contrib.sync.django.mixin import SyncableMixin


logger = logging.getLogger(__name__)

_RACE_RETRIES_MAX = 5
_RACE_RETRY_DELAY = 0.01


class UpsertStrategy(Protocol):
    def apply(
        self,
        model: type[SyncableMixin],
        key: str,
        sync_record: SyncRecord,
        field_data: dict[str, Any],
    ) -> bool: ...


class StalenessGuardedUpsertStrategy:
    def __init__(self, identity_field: str = 'id') -> None:
        self._identity_field = identity_field

    def _build_update_values(
        self,
        sync_record: SyncRecord,
        field_data: dict[str, Any],
    ) -> dict[str, Any]:
        values = {
            key: value
            for key, value in field_data.items()
            if key != self._identity_field
        }

        values['sync_field_timestamps'] = dict(sync_record.timestamps)
        values['sync_field_last_modified'] = sync_record.sync_field_last_modified

        return values

    def _force_auto_fields(
        self,
        model: type[SyncableMixin],
        key: str,
        field_data: dict[str, Any],
    ) -> None:
        auto_values: dict[str, Any] = {}

        for field in model._meta.concrete_fields:
            is_auto_add = getattr(
                field,
                'auto_now_add',
                False,
            )

            is_auto_now = getattr(
                field,
                'auto_now',
                False,
            )

            if not is_auto_add and not is_auto_now:
                continue

            attr_name = (
                field.attname
                if field.is_relation
                else field.name
            )

            if attr_name not in field_data:
                continue

            if field_data[attr_name] is None:
                continue

            auto_values[attr_name] = field_data[attr_name]

        if auto_values:
            identity_filter = {self._identity_field: key}
            model.objects.filter(**identity_filter).update(**auto_values)

    def _insert_with_race_fallback(
        self,
        model: type[SyncableMixin],
        key: str,
        sync_record: SyncRecord,
        field_data: dict[str, Any],
    ) -> bool:
        insert_data = dict(field_data)

        if self._identity_field not in insert_data:
            insert_data[self._identity_field] = key

        instance = model(**insert_data)
        instance.sync_field_timestamps = dict(sync_record.timestamps)
        instance.sync_field_last_modified = sync_record.sync_field_last_modified

        try:
            with transaction.atomic(), sync_bypass():
                instance.save(force_insert=True)
        except IntegrityError:
            return self._resolve_insert_race(
                model,
                key,
                sync_record,
                field_data,
            )
        else:
            self._force_auto_fields(model, key, field_data)
            return True

    def _resolve_insert_race(
        self,
        model: type[SyncableMixin],
        key: str,
        sync_record: SyncRecord,
        field_data: dict[str, Any],
    ) -> bool:
        for _ in range(_RACE_RETRIES_MAX):
            if self._update_if_stale(model, key, sync_record, field_data):
                return True

            if self._record_exists(model, key):
                return False

            time.sleep(_RACE_RETRY_DELAY)

        logger.warning(
            'Concurrent insert race for %s:%s: '
            'competing row not visible after %d retries',
            model._meta.label,
            key,
            _RACE_RETRIES_MAX,
        )

        return False

    def _record_exists(
        self,
        model: type[SyncableMixin],
        key: str,
    ) -> bool:
        identity_filter = {self._identity_field: key}
        return model.objects.filter(**identity_filter).exists()

    def _update_if_stale(
        self,
        model: type[SyncableMixin],
        key: str,
        sync_record: SyncRecord,
        field_data: dict[str, Any],
    ) -> bool:
        update_values = self._build_update_values(
            sync_record,
            field_data,
        )

        staleness_filter = {
            self._identity_field: key,
            'sync_field_last_modified__lte': (
                sync_record.sync_field_last_modified
            ),
        }

        updated = (
            model.objects
            .filter(**staleness_filter)
            .update(**update_values)
        )

        return updated > 0

    def apply(
        self,
        model: type[SyncableMixin],
        key: str,
        sync_record: SyncRecord,
        field_data: dict[str, Any],
    ) -> bool:
        if self._update_if_stale(model, key, sync_record, field_data):
            return True

        if self._record_exists(model, key):
            return False

        if not sync_record.timestamps:
            logger.warning(
                'Skipping ghost record %s for %s: '
                'empty timestamps would create a record '
                'with sync_field_last_modified=0',
                key,
                model._meta.label,
            )

            return False

        return self._insert_with_race_fallback(
            model,
            key,
            sync_record,
            field_data,
        )
