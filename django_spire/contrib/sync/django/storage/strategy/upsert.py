from __future__ import annotations

import logging
import time

from typing import Any, Protocol, TYPE_CHECKING

from django.db import IntegrityError, connections, router, transaction

from django_spire.contrib.sync.django.queryset import sync_bypass

if TYPE_CHECKING:
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.models import Field

    from django_spire.contrib.sync.database.record import SyncRecord
    from django_spire.contrib.sync.django.mixin import SyncableMixin


logger = logging.getLogger(__name__)

_RACE_RETRIES_MAX = 5
_RACE_RETRY_DELAY = 0.01

_SUPPORTED_VENDORS = frozenset({'postgresql', 'sqlite'})
_PARAM_LIMIT = 30_000


class UpsertStrategy(Protocol):
    def apply_many(
        self,
        model: type[SyncableMixin],
        records: dict[str, SyncRecord],
        deserialized: dict[str, dict[str, Any]],
    ) -> set[str]: ...


class BulkUpsertStrategy:
    def __init__(self, identity_field: str = 'id') -> None:
        self._identity_field = identity_field

    def _build_instance(
        self,
        model: type[SyncableMixin],
        key: str,
        sync_record: SyncRecord,
        field_data: dict[str, Any],
    ) -> SyncableMixin:
        data = dict(field_data)

        if self._identity_field not in data:
            data[self._identity_field] = key

        instance = model(**data)
        instance.sync_field_timestamps = dict(sync_record.timestamps)
        instance.sync_field_last_modified = sync_record.sync_field_last_modified

        return instance

    def _build_row_params(
        self,
        instance: SyncableMixin,
        fields: list[Field],
        connection: BaseDatabaseWrapper,
    ) -> list[Any]:
        return [
            field.get_db_prep_save(
                getattr(instance, field.attname),
                connection,
            )
            for field in fields
        ]

    def _build_sql(
        self,
        model: type[SyncableMixin],
        fields: list[Field],
        connection: BaseDatabaseWrapper,
        row_count: int,
    ) -> str:
        quote = connection.ops.quote_name
        table = quote(model._meta.db_table)

        identity_column = quote(
            model._meta.get_field(self._identity_field).column,
        )

        last_modified_column = quote(
            model._meta.get_field('sync_field_last_modified').column,
        )

        columns = [quote(field.column) for field in fields]

        placeholder_row = (
            '(' + ', '.join(['%s'] * len(fields)) + ')'
        )

        values_clause = ', '.join(
            [placeholder_row] * row_count,
        )

        set_clause = ', '.join(
            f'{col} = EXCLUDED.{col}'
            for col in columns
            if col != identity_column
        )

        return (
            f'INSERT INTO {table} ({", ".join(columns)}) '
            f'VALUES {values_clause} '
            f'ON CONFLICT ({identity_column}) '
            f'DO UPDATE SET {set_clause} '
            f'WHERE {table}.{last_modified_column} '
            f'<= EXCLUDED.{last_modified_column} '
            f'RETURNING {identity_column}'
        )

    def _connection(
        self,
        model: type[SyncableMixin],
    ) -> BaseDatabaseWrapper:
        db_alias = router.db_for_write(model) or 'default'

        return connections[db_alias]

    def _filter_ghosts(
        self,
        records: dict[str, SyncRecord],
    ) -> tuple[dict[str, SyncRecord], set[str]]:
        writable: dict[str, SyncRecord] = {}
        skipped: set[str] = set()

        for key in sorted(records.keys()):
            sync_record = records[key]

            if not sync_record.timestamps:
                logger.warning(
                    'Skipping ghost record %s: empty timestamps',
                    key,
                )

                skipped.add(key)
                continue

            writable[key] = sync_record

        return writable, skipped

    def _rows_per_batch(self, field_count: int) -> int:
        return max(1, _PARAM_LIMIT // field_count)

    def _writable_fields(
        self,
        model: type[SyncableMixin],
    ) -> list[Field]:
        return list(model._meta.concrete_fields)

    def apply_many(
        self,
        model: type[SyncableMixin],
        records: dict[str, SyncRecord],
        deserialized: dict[str, dict[str, Any]],
    ) -> set[str]:
        if not records:
            return set()

        connection = self._connection(model)

        if connection.vendor not in _SUPPORTED_VENDORS:
            message = (
                f'BulkUpsertStrategy requires postgresql or sqlite, '
                f'got {connection.vendor!r}'
            )

            raise NotImplementedError(message)

        writable, skipped = self._filter_ghosts(records)

        if not writable:
            return skipped

        fields = self._writable_fields(model)
        sorted_keys = sorted(writable.keys())

        instances = [
            self._build_instance(
                model,
                key,
                writable[key],
                deserialized[key],
            )
            for key in sorted_keys
        ]

        identity = model._meta.get_field(self._identity_field)
        rows_per_batch = self._rows_per_batch(len(fields))
        applied: set[str] = set()

        with sync_bypass(), connection.cursor() as cursor:
            for offset in range(0, len(instances), rows_per_batch):
                batch = instances[offset:offset + rows_per_batch]

                params: list[Any] = []

                for instance in batch:
                    params.extend(
                        self._build_row_params(
                            instance,
                            fields,
                            connection,
                        ),
                    )

                sql = self._build_sql(
                    model,
                    fields,
                    connection,
                    len(batch),
                )

                cursor.execute(sql, params)

                applied.update(
                    str(identity.to_python(row[0]))
                    for row in cursor.fetchall()
                )

        for key in writable:
            if key not in applied:
                skipped.add(key)

        return skipped


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

        values['sync_field_timestamps'] = dict(
            sync_record.timestamps,
        )
        values['sync_field_last_modified'] = (
            sync_record.sync_field_last_modified
        )

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

        instance.sync_field_timestamps = dict(
            sync_record.timestamps,
        )

        instance.sync_field_last_modified = (
            sync_record.sync_field_last_modified
        )

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

    def _record_exists(
        self,
        model: type[SyncableMixin],
        key: str,
    ) -> bool:
        identity_filter = {self._identity_field: key}
        return model.objects.filter(**identity_filter).exists()

    def _resolve_insert_race(
        self,
        model: type[SyncableMixin],
        key: str,
        sync_record: SyncRecord,
        field_data: dict[str, Any],
    ) -> bool:
        for _ in range(_RACE_RETRIES_MAX):
            if self._update_if_stale(
                model,
                key,
                sync_record,
                field_data,
            ):
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

    def _apply_one(
        self,
        model: type[SyncableMixin],
        key: str,
        sync_record: SyncRecord,
        field_data: dict[str, Any],
    ) -> bool:
        if self._update_if_stale(
            model,
            key,
            sync_record,
            field_data,
        ):
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

    def apply_many(
        self,
        model: type[SyncableMixin],
        records: dict[str, SyncRecord],
        deserialized: dict[str, dict[str, Any]],
    ) -> set[str]:
        skipped: set[str] = set()

        for key in sorted(records.keys()):
            sync_record = records[key]
            field_data = deserialized[key]

            applied = self._apply_one(
                model,
                key,
                sync_record,
                field_data,
            )

            if not applied:
                skipped.add(key)

        return skipped
