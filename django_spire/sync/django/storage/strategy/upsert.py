from __future__ import annotations

import logging
import time

from typing import Any, Protocol, TYPE_CHECKING

from django.db import IntegrityError, connections, router, transaction

from django_spire.sync.core.model import Error
from django_spire.sync.database.record import RecordContext
from django_spire.sync.database.storage import UpsertResult
from django_spire.sync.django.queryset import sync_bypass

if TYPE_CHECKING:
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.models import Field

    from django_spire.sync.database.record import SyncRecord
    from django_spire.sync.django.mixin import SyncableMixin


logger = logging.getLogger(__name__)

_RACE_RETRIES_MAX = 5
_RACE_RETRY_DELAY = 0.01

_SUPPORTED_VENDORS = frozenset({'postgresql', 'sqlite'})
_PARAMETER_LIMIT = 30_000


class UpsertStrategy(Protocol):
    def apply_many(
        self,
        model: type[SyncableMixin],
        records: dict[str, SyncRecord],
        deserialized: dict[str, dict[str, Any]],
        origin_node: str,
    ) -> UpsertResult: ...


class BulkUpsertStrategy:
    def __init__(self, identity_field: str = 'id') -> None:
        self._identity_field = identity_field

    def _build_instance(self, ctx: RecordContext) -> SyncableMixin:
        data = dict(ctx.field_data)

        if self._identity_field not in data:
            data[self._identity_field] = ctx.key

        instance = ctx.model(**data)
        instance.sync_field_timestamps = dict(ctx.sync_record.timestamps)
        instance.sync_field_last_modified = ctx.sync_record.sync_field_last_modified
        instance.sync_field_sequence = ctx.sequence
        instance.sync_field_origin_node = ctx.origin_node

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

    def _build_upsert_sql(
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

        column_last_modified = quote(
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
            f'{column} = EXCLUDED.{column}'
            for column in columns
            if column != identity_column
        )

        return (
            f'INSERT INTO {table} ({", ".join(columns)}) '
            f'VALUES {values_clause} '
            f'ON CONFLICT ({identity_column}) '
            f'DO UPDATE SET {set_clause} '
            f'WHERE {table}.{column_last_modified} '
            f'<= EXCLUDED.{column_last_modified} '
            f'RETURNING {identity_column}'
        )

    def _connection(
        self,
        model: type[SyncableMixin],
    ) -> BaseDatabaseWrapper:
        db_alias = router.db_for_write(model) or 'default'
        return connections[db_alias]

    def _validate_records(
        self,
        model_label: str,
        records: dict[str, SyncRecord],
    ) -> tuple[dict[str, SyncRecord], list[Error]]:
        writable: dict[str, SyncRecord] = {}
        errors: list[Error] = []

        for key in sorted(records.keys()):
            sync_record = records[key]

            if sync_record.sync_field_last_modified == 0:
                message = (
                    f'Ghost record for {model_label} key={key}: '
                    f'sync_field_last_modified=0 indicates record was '
                    f'never properly stamped '
                    f'(timestamps={sync_record.timestamps!r}, '
                    f'received_at={sync_record.received_at}). '
                    f'Run stamp_unstamped_records on the source node '
                    f'or check that AppConfig.ready() runs.'
                )

                logger.error(message)

                errors.append(Error(key=key, message=message))
                continue

            writable[key] = sync_record

        return writable, errors

    def _rows_per_batch(self, field_count: int) -> int:
        return max(1, _PARAMETER_LIMIT // field_count)

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
        origin_node: str,
    ) -> UpsertResult:
        if not records:
            return UpsertResult()

        connection = self._connection(model)

        if connection.vendor not in _SUPPORTED_VENDORS:
            message = (
                f'BulkUpsertStrategy requires postgresql or sqlite, '
                f'got {connection.vendor!r}'
            )

            raise NotImplementedError(message)

        model_label = model._meta.label
        writable, errors = self._validate_records(model_label, records)

        if not writable:
            return UpsertResult(skipped=set(), errors=errors)

        from django_spire.sync.django.sequence import (  # noqa: PLC0415
            SyncSequenceAllocator,
        )

        fields = self._writable_fields(model)
        sorted_keys = sorted(writable.keys())

        sequence_first = SyncSequenceAllocator().allocate(len(sorted_keys)).value_first

        instances = [
            self._build_instance(RecordContext(
                model=model,
                key=key,
                sync_record=writable[key],
                field_data=deserialized[key],
                sequence=sequence_first + index,
                origin_node=origin_node,
            ))
            for index, key in enumerate(sorted_keys)
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

                sql = self._build_upsert_sql(
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

        skipped: set[str] = set()

        for key in writable:
            if key not in applied:
                skipped.add(key)

        return UpsertResult(skipped=skipped, errors=errors)


class StalenessGuardedUpsertStrategy:
    def __init__(self, identity_field: str = 'id') -> None:
        self._identity_field = identity_field

    def _build_update_values(self, ctx: RecordContext) -> dict[str, Any]:
        values = {
            key: value
            for key, value in ctx.field_data.items()
            if key != self._identity_field
        }

        values['sync_field_timestamps'] = dict(
            ctx.sync_record.timestamps,
        )

        values['sync_field_last_modified'] = (
            ctx.sync_record.sync_field_last_modified
        )

        values['sync_field_sequence'] = ctx.sequence
        values['sync_field_origin_node'] = ctx.origin_node

        return values

    def _force_auto_fields(self, ctx: RecordContext) -> None:
        auto_values: dict[str, Any] = {}

        for field in ctx.model._meta.concrete_fields:
            is_auto_add = getattr(field, 'auto_now_add', False)
            is_auto_now = getattr(field, 'auto_now', False)

            if not is_auto_add and not is_auto_now:
                continue

            attribute_name = (
                field.attname
                if field.is_relation
                else field.name
            )

            if attribute_name not in ctx.field_data:
                continue

            if ctx.field_data[attribute_name] is None:
                continue

            auto_values[attribute_name] = ctx.field_data[attribute_name]

        if auto_values:
            identity_filter = {self._identity_field: ctx.key}
            ctx.model.objects.filter(**identity_filter).update(**auto_values)

    def _insert_with_race_fallback(self, ctx: RecordContext) -> bool:
        data = dict(ctx.field_data)
        data[self._identity_field] = ctx.key

        instance = ctx.model(**data)
        instance.sync_field_timestamps = dict(ctx.sync_record.timestamps)
        instance.sync_field_last_modified = ctx.sync_record.sync_field_last_modified
        instance.sync_field_sequence = ctx.sequence
        instance.sync_field_origin_node = ctx.origin_node

        for attempt in range(_RACE_RETRIES_MAX):
            try:
                with sync_bypass(), transaction.atomic():
                    instance.save(force_insert=True)
            except IntegrityError:
                if self._update_if_stale(ctx):
                    return True

                if attempt < _RACE_RETRIES_MAX - 1:
                    time.sleep(_RACE_RETRY_DELAY)
                    continue

                return False
            else:
                self._force_auto_fields(ctx)
                return True

        return False

    def _record_exists(self, ctx: RecordContext) -> bool:
        identity_filter = {self._identity_field: ctx.key}
        return ctx.model.objects.filter(**identity_filter).exists()

    def _update_if_stale(self, ctx: RecordContext) -> bool:
        staleness_filter = {
            self._identity_field: ctx.key,
            'sync_field_last_modified__lte': ctx.sync_record.sync_field_last_modified,
        }

        values = self._build_update_values(ctx)

        with sync_bypass():
            updated = ctx.model.objects.filter(**staleness_filter).update(**values)

        if updated:
            self._force_auto_fields(ctx)

        return updated > 0

    def _apply_one(self, ctx: RecordContext) -> bool:
        if self._update_if_stale(ctx):
            return True

        if self._record_exists(ctx):
            return False

        return self._insert_with_race_fallback(ctx)

    def apply_many(
        self,
        model: type[SyncableMixin],
        records: dict[str, SyncRecord],
        deserialized: dict[str, dict[str, Any]],
        origin_node: str,
    ) -> UpsertResult:
        from django_spire.sync.django.sequence import (  # noqa: PLC0415
            SyncSequenceAllocator,
        )

        skipped: set[str] = set()
        errors: list[Error] = []
        sorted_keys = sorted(records.keys())

        if not sorted_keys:
            return UpsertResult()

        sequence_first = SyncSequenceAllocator().allocate(len(sorted_keys)).value_first

        for index, key in enumerate(sorted_keys):
            sync_record = records[key]
            field_data = deserialized[key]

            if sync_record.sync_field_last_modified == 0:
                message = (
                    f'Ghost record for {model._meta.label} key={key}: '
                    f'sync_field_last_modified=0 indicates record was '
                    f'never properly stamped '
                    f'(timestamps={sync_record.timestamps!r}, '
                    f'received_at={sync_record.received_at}). '
                    f'Run stamp_unstamped_records on the source node '
                    f'or check that AppConfig.ready() runs.'
                )

                logger.error(message)
                errors.append(Error(key=key, message=message))
                continue

            ctx = RecordContext(
                model=model,
                key=key,
                sync_record=sync_record,
                field_data=field_data,
                sequence=sequence_first + index,
                origin_node=origin_node,
            )

            if not self._apply_one(ctx):
                skipped.add(key)

        return UpsertResult(skipped=skipped, errors=errors)
