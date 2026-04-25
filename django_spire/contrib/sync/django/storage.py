from __future__ import annotations

import logging
import uuid

from typing import Any, TYPE_CHECKING

from django.core.exceptions import FieldDoesNotExist
from django.db import IntegrityError, transaction

from django_spire.contrib.sync.core.exceptions import (
    BatchLimitError,
    InvalidParameterError,
    UnknownModelError,
)
from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.database.storage import DatabaseSyncStorage
from django_spire.contrib.sync.django.models.checkpoint import SyncCheckpoint
from django_spire.contrib.sync.django.queryset import sync_bypass

if TYPE_CHECKING:
    from django_spire.contrib.sync.core.clock import HybridLogicalClock
    from django_spire.contrib.sync.django.mixin import SyncableMixin


logger = logging.getLogger(__name__)

_BATCH_SIZE_MAX = 5_000


class DjangoSyncStorage(DatabaseSyncStorage):
    def __init__(
        self,
        models: list[type[SyncableMixin]],
        clock: HybridLogicalClock,
        identity_field: str = 'id',
        batch_size_max: int = _BATCH_SIZE_MAX,
    ) -> None:
        if batch_size_max < 1:
            message = f'batch_size_max must be >= 1, got {batch_size_max}'
            raise InvalidParameterError(message)

        self._batch_size_max = batch_size_max
        self._clock = clock
        self._identity_field = identity_field
        self._models: dict[str, type[SyncableMixin]] = {
            model._meta.label: model for model in models
        }

    def _check_batch_limit(self, count: int, operation: str) -> None:
        if count > self._batch_size_max:
            message = (
                f'{operation} received {count} items, '
                f'exceeds batch_size_max={self._batch_size_max}'
            )
            raise BatchLimitError(message)

    def _coerce_value(self, value: Any) -> Any:
        if isinstance(value, uuid.UUID):
            return str(value)

        return value

    def _get_many_to_many_names(self, model: type[SyncableMixin]) -> set[str]:
        return {field.name for field in model._meta.many_to_many}

    def _get_model(self, model_label: str) -> type[SyncableMixin]:
        model = self._models.get(model_label)

        if model is None:
            message = f'Unknown syncable model: {model_label!r}'
            raise UnknownModelError(message)

        return model

    def _has_field(
        self,
        model: type[SyncableMixin],
        field_name: str,
    ) -> bool:
        try:
            model._meta.get_field(field_name)
        except FieldDoesNotExist:
            return False
        else:
            return True

    def _instance_to_record(self, instance: SyncableMixin) -> SyncRecord:
        data: dict[str, Any] = {}

        for field in instance._meta.concrete_fields:
            value = getattr(instance, field.attname)
            data[field.name] = self._coerce_value(value)

        for field in instance._meta.many_to_many:
            related = getattr(instance, field.name)
            data[field.name] = sorted(
                str(related_instance.pk)
                for related_instance in related.all()
            )

        key = str(getattr(instance, self._identity_field))
        timestamps = dict(instance.sync_field_timestamps)

        return SyncRecord(key=key, data=data, timestamps=timestamps)

    def _split_fields(
        self,
        sync_record: SyncRecord,
        many_to_many_names: set[str],
    ) -> tuple[dict[str, Any], dict[str, list[Any]]]:
        field_data: dict[str, Any] = {}
        many_to_many_data: dict[str, list[Any]] = {}

        for field_key, field_value in sync_record.data.items():
            if field_key in many_to_many_names:
                many_to_many_data[field_key] = field_value
            else:
                field_data[field_key] = field_value

        return field_data, many_to_many_data

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

    def _upsert_one(
        self,
        model: type[SyncableMixin],
        key: str,
        sync_record: SyncRecord,
        many_to_many_names: set[str],
    ) -> tuple[bool, dict[str, list[Any]]]:
        incoming_lm = sync_record.sync_field_last_modified
        field_data, many_to_many_data = self._split_fields(
            sync_record, many_to_many_names,
        )

        update_values = self._build_update_values(sync_record, field_data)

        updated = model.objects.filter(
            **{self._identity_field: key},
            sync_field_last_modified__lte=incoming_lm,
        ).update(**update_values)

        if updated > 0:
            return False, many_to_many_data

        exists = model.objects.filter(
            **{self._identity_field: key},
        ).exists()

        if exists:
            return True, {}

        if not sync_record.timestamps:
            logger.warning(
                'Skipping ghost record %s for %s: empty timestamps '
                'would create a record with sync_field_last_modified=0',
                key,
                model._meta.label,
            )
            return True, {}

        insert_data = dict(field_data)

        if self._identity_field not in insert_data:
            insert_data[self._identity_field] = key

        instance = model(**insert_data)
        instance.sync_field_timestamps = dict(sync_record.timestamps)
        instance.sync_field_last_modified = incoming_lm

        try:
            with transaction.atomic(), sync_bypass():
                instance.save(force_insert=True)
        except IntegrityError:
            updated = model.objects.filter(
                **{self._identity_field: key},
                sync_field_last_modified__lte=incoming_lm,
            ).update(**update_values)

            if updated == 0:
                return True, {}

        return False, many_to_many_data

    def _apply_many_to_many(
        self,
        model: type[SyncableMixin],
        pending: dict[str, dict[str, list[Any]]],
    ) -> set[str]:
        skipped: set[str] = set()

        if not pending:
            return skipped

        lookup = {
            f'{self._identity_field}__in': list(pending.keys()),
        }

        instances_by_key = {
            str(getattr(instance, self._identity_field)): instance
            for instance in model.objects.filter(**lookup)
        }

        with sync_bypass():
            for key in sorted(pending.keys()):
                many_to_many_data = pending[key]
                instance = instances_by_key.get(key)

                if instance is None:
                    logger.warning(
                        'Skipping M2M relations for %s key=%s: '
                        'instance not found after upsert',
                        model._meta.label,
                        key,
                    )
                    skipped.add(key)
                    continue

                for field_name, values in sorted(many_to_many_data.items()):
                    try:
                        getattr(instance, field_name).set(values)
                    except IntegrityError:
                        logger.exception(
                            'M2M set failed for %s:%s field=%s values=%s',
                            model._meta.label,
                            key,
                            field_name,
                            values,
                        )
                        raise

        return skipped

    def delete_many(
        self,
        model_label: str,
        deletes: dict[str, int],
    ) -> None:
        if not deletes:
            return

        self._check_batch_limit(len(deletes), 'delete_many')

        model = self._get_model(model_label)

        if not self._has_field(model, 'is_deleted'):
            self._hard_delete_many(model, deletes)
            return

        self._soft_delete_many(model, deletes)

    def _hard_delete_many(
        self,
        model: type[SyncableMixin],
        deletes: dict[str, int],
    ) -> None:
        with transaction.atomic():
            existing = {
                str(pk): lm
                for pk, lm in model.objects.select_for_update().filter(
                    **{f'{self._identity_field}__in': list(deletes.keys())},
                ).values_list(self._identity_field, 'sync_field_last_modified')
            }

            keys_to_delete: list[str] = []

            for key, tombstone_ts in deletes.items():
                existing_lm = existing.get(key)

                if existing_lm is None:
                    continue

                if existing_lm <= tombstone_ts:
                    keys_to_delete.append(key)
                else:
                    logger.info(
                        'Skipping hard delete for %s:%s: '
                        'local modified after tombstone',
                        model._meta.label,
                        key,
                    )

            if keys_to_delete:
                model.objects.filter(
                    **{f'{self._identity_field}__in': keys_to_delete},
                ).delete()

    def _soft_delete_many(
        self,
        model: type[SyncableMixin],
        deletes: dict[str, int],
    ) -> None:
        with transaction.atomic():
            instances = list(
                model.objects.select_for_update().filter(
                    **{f'{self._identity_field}__in': list(deletes.keys())},
                ),
            )

            to_update: list[SyncableMixin] = []

            for instance in instances:
                key = str(getattr(instance, self._identity_field))
                tombstone_ts = deletes[key]

                if instance.sync_field_last_modified > tombstone_ts:
                    logger.info(
                        'Skipping soft delete for %s:%s: '
                        'local modified after tombstone',
                        model._meta.label,
                        key,
                    )
                    continue

                timestamps = dict(instance.sync_field_timestamps)
                timestamps['is_deleted'] = tombstone_ts
                instance.sync_field_timestamps = timestamps
                instance.sync_field_last_modified = tombstone_ts
                instance.is_deleted = True
                to_update.append(instance)

            if to_update:
                with sync_bypass():
                    model.objects.bulk_update(
                        to_update,
                        ['is_deleted', 'sync_field_timestamps', 'sync_field_last_modified'],
                    )

    def get_changed_since(
        self,
        model_label: str,
        timestamp: int,
    ) -> dict[str, SyncRecord]:
        model = self._get_model(model_label)
        many_to_many_names = self._get_many_to_many_names(model)

        queryset = model.objects.filter(sync_field_last_modified__gt=timestamp)

        if many_to_many_names:
            queryset = queryset.prefetch_related(*many_to_many_names)

        return {
            str(getattr(instance, self._identity_field)):
                self._instance_to_record(instance)
            for instance in queryset
        }

    def get_checkpoint(self, node_id: str) -> int:
        checkpoint = SyncCheckpoint.objects.filter(
            node_id=node_id,
        ).first()

        if checkpoint is None:
            return 0

        return checkpoint.timestamp

    def get_records(
        self,
        model_label: str,
        keys: set[str],
    ) -> dict[str, SyncRecord]:
        if not keys:
            return {}

        model = self._get_model(model_label)
        many_to_many_names = self._get_many_to_many_names(model)

        queryset = model.objects.filter(
            **{f'{self._identity_field}__in': keys},
        )

        if many_to_many_names:
            queryset = queryset.prefetch_related(*many_to_many_names)

        return {
            str(getattr(instance, self._identity_field)):
                self._instance_to_record(instance)
            for instance in queryset
        }

    def get_syncable_models(self) -> list[str]:
        return sorted(self._models.keys())

    def save_checkpoint(self, node_id: str, timestamp: int) -> None:
        SyncCheckpoint.objects.update_or_create(
            node_id=node_id,
            defaults={'timestamp': timestamp},
        )

    def upsert_many(
        self,
        model_label: str,
        records: dict[str, SyncRecord],
    ) -> set[str]:
        self._check_batch_limit(len(records), 'upsert_many')

        if not records:
            return set()

        model = self._get_model(model_label)
        many_to_many_names = self._get_many_to_many_names(model)

        skipped: set[str] = set()
        pending_many_to_many: dict[str, dict[str, list[Any]]] = {}

        with transaction.atomic():
            for key in sorted(records.keys()):
                sync_record = records[key]
                was_skipped, many_to_many_data = self._upsert_one(
                    model, key, sync_record, many_to_many_names,
                )

                if was_skipped:
                    skipped.add(key)
                    continue

                if many_to_many_data:
                    pending_many_to_many[key] = many_to_many_data

            if pending_many_to_many:
                m2m_skipped = self._apply_many_to_many(
                    model, pending_many_to_many,
                )
                skipped |= m2m_skipped

        return skipped
