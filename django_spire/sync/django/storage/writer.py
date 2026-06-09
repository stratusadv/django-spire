from __future__ import annotations

import json
import logging

from collections import defaultdict
from typing import Any, TYPE_CHECKING

from django.core.exceptions import FieldDoesNotExist
from django.db import connections, router, transaction

from django_spire.sync.core.exceptions import (
    BatchLimitError,
    InvalidParameterError,
    UnknownModelError,
)
from django_spire.sync.database.storage import UpsertResult
from django_spire.sync.django.serializer import SyncFieldSerializer
from django_spire.sync.django.storage.many_to_many import ManyToManyApplier
from django_spire.sync.django.storage.strategy import (
    BulkUpsertStrategy,
    DeleteStrategy,
    HardDeleteStrategy,
    SoftDeleteStrategy,
    UpsertStrategy,
)

if TYPE_CHECKING:
    from django.db.backends.base.base import BaseDatabaseWrapper

    from django_spire.sync.core.clock import HybridLogicalClock
    from django_spire.sync.core.model import Error
    from django_spire.sync.database.record import SyncRecord
    from django_spire.sync.django.graph import DeferredForeignKey
    from django_spire.sync.django.mixin import SyncableMixin


logger = logging.getLogger(__name__)

_BATCH_SIZE_MAX = 5_000
_PARAMETER_LIMIT = 30_000


def _field_by_attribute_name(model: type[SyncableMixin], attribute_name: str) -> Any:
    for field in model._meta.concrete_fields:
        if field.attname == attribute_name:
            return field

    message = f'No field with attribute name {attribute_name!r} on {model._meta.label}'

    raise FieldDoesNotExist(message)


class DjangoRecordWriter:
    def __init__(
        self,
        models: list[type[SyncableMixin]],
        identity_field: str = 'id',
        batch_size_max: int = _BATCH_SIZE_MAX,
        deferred_foreign_keys: list[DeferredForeignKey] | None = None,
        delete_strategies: dict[str, DeleteStrategy] | None = None,
        many_to_many_applier: ManyToManyApplier | None = None,
        upsert_strategy: UpsertStrategy | None = None,
    ) -> None:
        if not models:
            message = 'models must not be empty'
            raise InvalidParameterError(message)

        if not identity_field:
            message = 'identity_field must be a non-empty string'
            raise InvalidParameterError(message)

        if batch_size_max < 1:
            message = f'batch_size_max must be >= 1, got {batch_size_max}'

            raise InvalidParameterError(message)

        self._batch_size_max = batch_size_max
        self._identity_field = identity_field

        self._models: dict[str, type[SyncableMixin]] = {
            model._meta.label: model for model in models
        }

        self._serializers: dict[str, SyncFieldSerializer] = {
            model._meta.label: SyncFieldSerializer(model) for model in models
        }

        self._upsert_strategy = upsert_strategy or BulkUpsertStrategy(identity_field=identity_field)

        self._many_to_many_applier = many_to_many_applier or ManyToManyApplier(
            identity_field=identity_field
        )

        self._delete_strategies = delete_strategies or self._build_delete_strategies(models)

        self._deferred_attribute_names: dict[str, set[str]] = defaultdict(set)

        self._external_nullable_attribute_names: dict[str, set[str]] = defaultdict(set)

        syncable_labels = set(self._models.keys())

        for deferred_foreign_key in deferred_foreign_keys or []:
            if deferred_foreign_key.target_label in syncable_labels:
                self._deferred_attribute_names[deferred_foreign_key.source_label].add(
                    deferred_foreign_key.attribute_name
                )
            else:
                self._external_nullable_attribute_names[deferred_foreign_key.source_label].add(
                    deferred_foreign_key.attribute_name
                )

    def _build_assign_sequence_sql(self, table: str, id_column: str) -> str:
        return (
            f'WITH ranked AS ('
            f'  SELECT {id_column} AS pk, '
            f'    ROW_NUMBER() OVER ('
            f'      ORDER BY sync_field_last_modified, {id_column}'
            f'    ) + %s - 1 AS seq '
            f'  FROM {table} '
            f'  WHERE sync_field_sequence = 0'
            f') '
            f'UPDATE {table} '
            f'SET sync_field_sequence = ranked.seq '
            f'FROM ranked '
            f'WHERE {table}.{id_column} = ranked.pk'
        )

    def _build_column_check_sql(self) -> str:
        return (
            'SELECT COUNT(*) '
            'FROM information_schema.columns '
            'WHERE table_name = %s '
            "AND column_name = 'sync_field_sequence'"
        )

    def _build_delete_strategies(
        self, models: list[type[SyncableMixin]]
    ) -> dict[str, DeleteStrategy]:
        soft = SoftDeleteStrategy(identity_field=self._identity_field)
        hard = HardDeleteStrategy(identity_field=self._identity_field)

        return {
            model._meta.label: (soft if self._has_field(model, 'is_deleted') else hard)
            for model in models
        }

    def _build_ensure_sync_columns_sql(
        self, connection: BaseDatabaseWrapper, table_name: str
    ) -> list[str]:
        quote = connection.ops.quote_name
        table = quote(table_name)

        return [
            (
                f'ALTER TABLE {table} '
                f'ADD COLUMN IF NOT EXISTS sync_field_last_modified '
                f'BIGINT NOT NULL DEFAULT 0'
            ),
            (
                f'ALTER TABLE {table} '
                f'ADD COLUMN IF NOT EXISTS sync_field_timestamps '
                f"JSONB NOT NULL DEFAULT '{{}}'"
            ),
            (f'ALTER TABLE {table} ADD COLUMN sync_field_sequence BIGINT NOT NULL DEFAULT 0'),
            (
                f'ALTER TABLE {table} '
                f'ADD COLUMN sync_field_origin_node '
                f"VARCHAR(255) NOT NULL DEFAULT ''"
            ),
            (
                f'CREATE INDEX IF NOT EXISTS '
                f'{table_name}_lm_idx ON {table} '
                f'(sync_field_last_modified)'
            ),
            (f'CREATE INDEX {table_name}_seq_idx ON {table} (sync_field_sequence)'),
        ]

    def _build_foreign_key_backfill_sql(
        self,
        table: str,
        foreign_key_column: str,
        foreign_key_type: str,
        id_column: str,
        id_type: str,
        row_count: int,
    ) -> str:
        placeholders = ', '.join(['(%s, %s)'] * row_count)

        return (
            f'UPDATE {table} '
            f'SET {foreign_key_column} = '
            f'_v.val::{foreign_key_type} '
            f'FROM (VALUES {placeholders}) '
            f'AS _v(pk, val) '
            f'WHERE {table}.{id_column} = '
            f'_v.pk::{id_type}'
        )

    def _build_stamp_modified_sql(self, table: str) -> str:
        return (
            f'UPDATE {table} '
            f'SET sync_field_last_modified = %s, '
            f'    sync_field_timestamps = %s::jsonb '
            f'WHERE sync_field_last_modified = 0'
        )

    def _build_zero_field_count_sql(self, table: str, column: str) -> str:
        return f'SELECT COUNT(*) FROM {table} WHERE {column} = 0'

    def _check_batch_limit(self, count: int, operation: str) -> None:
        if count > self._batch_size_max:
            message = (
                f'{operation} received {count} items, exceeds batch_size_max={self._batch_size_max}'
            )

            raise BatchLimitError(message)

    def _ensure_sync_columns(self, labels: list[str]) -> None:
        for model_label in labels:
            if model_label not in self._models:
                continue

            model = self._models[model_label]

            connection = connections[router.db_for_write(model) or 'default']

            table_name = model._meta.db_table

            with connection.cursor() as cursor:
                cursor.execute(self._build_column_check_sql(), [table_name])

                if cursor.fetchone()[0] > 0:
                    continue

                statements = self._build_ensure_sync_columns_sql(connection, table_name)

                for statement in statements:
                    cursor.execute(statement)

                logger.info('Added sync columns to %s', table_name)

    def _extract_field_data(
        self, sync_record: SyncRecord, many_to_many_names: set[str]
    ) -> dict[str, Any]:
        return {
            key: value for key, value in sync_record.data.items() if key not in many_to_many_names
        }

    def _extract_many_to_many_data(
        self, sync_record: SyncRecord, many_to_many_names: set[str]
    ) -> dict[str, list[Any]]:
        return {key: value for key, value in sync_record.data.items() if key in many_to_many_names}

    def _get_many_to_many_names(self, model: type[SyncableMixin]) -> set[str]:
        return {field.name for field in model._meta.many_to_many}

    def _get_model(self, model_label: str) -> type[SyncableMixin]:
        model = self._models.get(model_label)

        if model is None:
            message = f'Unknown syncable model: {model_label!r}'
            raise UnknownModelError(message)

        return model

    def _has_field(self, model: type[SyncableMixin], field_name: str) -> bool:
        try:
            model._meta.get_field(field_name)
        except FieldDoesNotExist:
            return False
        else:
            return True

    def _nullify_deferred_columns(
        self, model_label: str, deserialized_row: dict[str, Any]
    ) -> dict[str, Any]:
        deferred_attribute_names = self._deferred_attribute_names.get(model_label)
        external_attribute_names = self._external_nullable_attribute_names.get(model_label)

        if external_attribute_names:
            for attribute_name in external_attribute_names:
                if attribute_name not in deserialized_row:
                    continue

                if deserialized_row[attribute_name] is None:
                    continue

                deserialized_row[attribute_name] = None

        if not deferred_attribute_names:
            return {}

        stashed: dict[str, Any] = {}

        for attribute_name in deferred_attribute_names:
            if attribute_name not in deserialized_row:
                continue

            value = deserialized_row[attribute_name]

            if value is None:
                continue

            stashed[attribute_name] = value
            deserialized_row[attribute_name] = None

        return stashed

    def _persist_deferred_backfill(
        self, model_label: str, stashes: dict[str, dict[str, Any]]
    ) -> None:
        from django_spire.sync.django.models.deferred_backfill import (  # noqa: PLC0415
            SyncDeferredBackfill,
        )

        rows: list[SyncDeferredBackfill] = []

        for record_key, attribute_name_values in stashes.items():
            for attribute_name, value in attribute_name_values.items():
                rows.append(
                    SyncDeferredBackfill(
                        model_label=model_label,
                        record_key=record_key,
                        attname=attribute_name,
                        fk_value=str(value),
                    )
                )

        if not rows:
            return

        SyncDeferredBackfill.objects.bulk_create(
            rows,
            update_conflicts=True,
            update_fields=['fk_value'],
            unique_fields=['model_label', 'record_key', 'attname'],
        )

    def _purge_deferred_backfill(self, model_label: str, record_keys: set[str]) -> None:
        if not record_keys:
            return

        from django_spire.sync.django.models.deferred_backfill import (  # noqa: PLC0415
            SyncDeferredBackfill,
        )

        SyncDeferredBackfill.objects.filter(
            model_label=model_label, record_key__in=list(record_keys)
        ).delete()

    def _reconcile_counter(self, labels: list[str]) -> None:
        from django.db.models import Max  # noqa: PLC0415
        from django_spire.sync.django.sequence import (  # noqa: PLC0415
            SyncSequenceAllocator,
        )

        sequence_max = 0

        for model_label in labels:
            if model_label not in self._models:
                continue

            model = self._models[model_label]

            result = model.objects.aggregate(sequence_max=Max('sync_field_sequence'))

            candidate = result['sequence_max'] or 0

            sequence_max = max(sequence_max, candidate)

        if sequence_max > 0:
            SyncSequenceAllocator().reconcile_to(sequence_max)

    def _run_backfill(
        self, model: type[SyncableMixin], key_columns: dict[str, dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        from django_spire.sync.django.queryset import sync_bypass  # noqa: PLC0415

        by_attribute_name: dict[str, list[tuple[str, Any]]] = defaultdict(list)

        for key, columns in key_columns.items():
            for attribute_name, value in columns.items():
                by_attribute_name[attribute_name].append((key, value))

        still_pending: dict[str, dict[str, Any]] = {}

        connection = connections[router.db_for_write(model) or 'default']

        for attribute_name, pairs in by_attribute_name.items():
            foreign_key_field = _field_by_attribute_name(model, attribute_name)
            target_model = foreign_key_field.related_model

            target_values = {str(value) for _, value in pairs}

            existing_targets = set(
                str(primary_key)
                for primary_key in target_model.objects.filter(pk__in=target_values).values_list(
                    'pk', flat=True
                )
            )

            can_backfill = [(key, value) for key, value in pairs if str(value) in existing_targets]

            for key, value in pairs:
                if str(value) not in existing_targets:
                    pending = still_pending.setdefault(key, {})
                    pending[attribute_name] = value

            if not can_backfill:
                continue

            quote = connection.ops.quote_name
            table = quote(model._meta.db_table)

            id_field = model._meta.get_field(self._identity_field)

            id_column = quote(id_field.column)
            foreign_key_column = quote(foreign_key_field.column)

            id_type = id_field.db_type(connection)
            foreign_key_type = foreign_key_field.db_type(connection)

            batch_limit = _PARAMETER_LIMIT // 2

            with sync_bypass(), connection.cursor() as cursor:
                for offset in range(0, len(can_backfill), batch_limit):
                    batch = can_backfill[offset : offset + batch_limit]

                    params: list[Any] = []

                    for key, value in batch:
                        params.append(id_field.get_db_prep_save(key, connection))
                        params.append(foreign_key_field.get_db_prep_save(value, connection))

                    sql = self._build_foreign_key_backfill_sql(
                        table, foreign_key_column, foreign_key_type, id_column, id_type, len(batch)
                    )

                    cursor.execute(sql, params)

        return still_pending

    def _upsert_chunk(
        self,
        model: type[SyncableMixin],
        records: dict[str, SyncRecord],
        chunk_keys: list[str],
        many_to_many_names: set[str],
        serializer: SyncFieldSerializer,
        origin_node: str,
    ) -> UpsertResult:
        chunk_records: dict[str, SyncRecord] = {}
        deserialized: dict[str, dict[str, Any]] = {}
        deferred_stashes: dict[str, dict[str, Any]] = {}
        pending_many_to_many: dict[str, dict[str, list[Any]]] = {}
        model_label = model._meta.label

        for key in chunk_keys:
            sync_record = records[key]
            chunk_records[key] = sync_record

            field_data = self._extract_field_data(sync_record, many_to_many_names)

            many_to_many_data = self._extract_many_to_many_data(sync_record, many_to_many_names)

            deserialized[key] = serializer.deserialize(field_data)

            stashed = self._nullify_deferred_columns(model_label, deserialized[key])

            if stashed:
                deferred_stashes[key] = stashed

            if many_to_many_data:
                pending_many_to_many[key] = many_to_many_data

        with transaction.atomic():
            if deferred_stashes:
                self._persist_deferred_backfill(model_label, deferred_stashes)

            upsert_result = self._upsert_strategy.apply_many(
                model, chunk_records, deserialized, origin_node
            )

            errored_keys = {error.key for error in upsert_result.errors}
            excluded = upsert_result.skipped | errored_keys

            if excluded:
                self._purge_deferred_backfill(model_label, excluded)

            for key in excluded:
                pending_many_to_many.pop(key, None)

            many_to_many_result = self._many_to_many_applier.apply(model, pending_many_to_many)

            upsert_result.skipped |= many_to_many_result.skipped
            upsert_result.errors.extend(many_to_many_result.errors)

        return upsert_result

    def clear_tombstones(self, model_label: str, keys: set[str]) -> None:
        if not keys:
            return

        from django_spire.sync.django.models.tombstone import SyncTombstone  # noqa: PLC0415

        SyncTombstone.objects.filter(model_label=model_label, record_key__in=keys).delete()

    def delete_many(self, model_label: str, deletes: dict[str, int], origin_node: str) -> None:
        if not deletes:
            return

        model = self._get_model(model_label)
        strategy = self._delete_strategies[model_label]
        keys = list(deletes.keys())

        for start in range(0, len(keys), self._batch_size_max):
            chunk_keys = keys[start : start + self._batch_size_max]
            chunk = {key: deletes[key] for key in chunk_keys}

            with transaction.atomic():
                strategy.delete(model, chunk, origin_node)

    def flush_deferred_backfill(self) -> None:
        from django_spire.sync.django.models.deferred_backfill import (  # noqa: PLC0415
            SyncDeferredBackfill,
        )

        rows = list(SyncDeferredBackfill.objects.all())

        if not rows:
            return

        by_label: dict[str, list[SyncDeferredBackfill]] = defaultdict(list)

        for row in rows:
            by_label[row.model_label].append(row)

        for model_label, label_rows in by_label.items():
            if model_label not in self._models:
                logger.warning(
                    'Skipping %d deferred backfill row(s) for unknown model %s',
                    len(label_rows),
                    model_label,
                )

                continue

            model = self._get_model(model_label)

            key_columns: dict[str, dict[str, Any]] = {}

            for row in label_rows:
                key_columns.setdefault(row.record_key, {})[row.attname] = row.fk_value

            still_pending = self._run_backfill(model, key_columns)

            ids_to_delete: list[int] = []

            for row in label_rows:
                still_pending_for_key = still_pending.get(row.record_key, {})

                if row.attname not in still_pending_for_key:
                    ids_to_delete.append(row.id)

            if ids_to_delete:
                SyncDeferredBackfill.objects.filter(id__in=ids_to_delete).delete()

            still_count = sum(len(values) for values in still_pending.values())

            if still_count:
                logger.debug(
                    '%d deferred FK backfill(s) still pending for %s (targets not yet present)',
                    still_count,
                    model_label,
                )

    def stamp_unstamped_records(
        self, clock: HybridLogicalClock, model_order: list[str] | None = None
    ) -> int:
        from django_spire.sync.django.queryset import sync_bypass  # noqa: PLC0415
        from django_spire.sync.django.sequence import (  # noqa: PLC0415
            SyncSequenceAllocator,
        )

        total = 0
        labels = model_order or sorted(self._models.keys())

        self._ensure_sync_columns(labels)
        self._reconcile_counter(labels)

        with sync_bypass():
            for model_label in labels:
                if model_label not in self._models:
                    continue

                model = self._models[model_label]

                connection = connections[router.db_for_write(model) or 'default']

                quote = connection.ops.quote_name
                table = quote(model._meta.db_table)

                id_field = model._meta.get_field(self._identity_field)

                id_column = quote(id_field.column)

                with connection.cursor() as cursor:
                    cursor.execute(self._build_zero_field_count_sql(table, 'sync_field_sequence'))

                    sequence_count = cursor.fetchone()[0]

                    cursor.execute(
                        self._build_zero_field_count_sql(table, 'sync_field_last_modified')
                    )

                    timestamp_count = cursor.fetchone()[0]

                if sequence_count == 0 and timestamp_count == 0:
                    continue

                stamp_timestamp = clock.now()

                stamp_field_names = list(model.get_syncable_field_names()) + list(
                    model.get_syncable_many_to_many_names()
                )

                stamp_timestamps_json = json.dumps(
                    dict.fromkeys(stamp_field_names, stamp_timestamp)
                )

                sequence_first = 0

                with transaction.atomic():
                    if sequence_count > 0:
                        sequence_first = (
                            SyncSequenceAllocator().allocate(sequence_count).value_first
                        )

                        with connection.cursor() as cursor:
                            cursor.execute(
                                self._build_assign_sequence_sql(table, id_column), [sequence_first]
                            )

                    if timestamp_count > 0:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                self._build_stamp_modified_sql(table),
                                [stamp_timestamp, stamp_timestamps_json],
                            )

                stamped = max(sequence_count, timestamp_count)

                logger.info(
                    'Stamped %s in %s (%d sequences from %d, %d timestamps, ts=%d)',
                    stamped,
                    model_label,
                    sequence_count,
                    sequence_first,
                    timestamp_count,
                    stamp_timestamp,
                )

                total += stamped

        return total

    def upsert_many(
        self, model_label: str, records: dict[str, SyncRecord], origin_node: str
    ) -> UpsertResult:
        if not records:
            return UpsertResult()

        model = self._get_model(model_label)
        many_to_many_names = self._get_many_to_many_names(model)
        serializer = self._serializers[model_label]

        skipped: set[str] = set()
        errors: list[Error] = []
        keys = sorted(records.keys())

        for start in range(0, len(keys), self._batch_size_max):
            chunk_keys = keys[start : start + self._batch_size_max]

            chunk_result = self._upsert_chunk(
                model, records, chunk_keys, many_to_many_names, serializer, origin_node
            )

            skipped |= chunk_result.skipped
            errors.extend(chunk_result.errors)

        return UpsertResult(skipped=skipped, errors=errors)
