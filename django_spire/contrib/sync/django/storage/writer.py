from __future__ import annotations

import logging

from typing import Any, TYPE_CHECKING

from django.core.exceptions import FieldDoesNotExist
from django.db import transaction

from django_spire.contrib.sync.core.exceptions import (
    BatchLimitError,
    InvalidParameterError,
    UnknownModelError,
)
from django_spire.contrib.sync.django.serializer import SyncFieldSerializer
from django_spire.contrib.sync.django.storage.many_to_many import ManyToManyApplier
from django_spire.contrib.sync.django.storage.strategy import (
    DeleteStrategy,
    HardDeleteStrategy,
    SoftDeleteStrategy,
    StalenessGuardedUpsertStrategy,
    UpsertStrategy,
)

if TYPE_CHECKING:
    from django_spire.contrib.sync.database.record import SyncRecord
    from django_spire.contrib.sync.django.mixin import SyncableMixin


logger = logging.getLogger(__name__)

_BATCH_SIZE_MAX = 5_000


class DjangoRecordWriter:
    def __init__(
        self,
        models: list[type[SyncableMixin]],
        identity_field: str = 'id',
        batch_size_max: int = _BATCH_SIZE_MAX,
        delete_strategies: dict[str, DeleteStrategy] | None = None,
        many_to_many_applier: ManyToManyApplier | None = None,
        upsert_strategy: UpsertStrategy | None = None,
    ) -> None:
        if batch_size_max < 1:
            message = f'batch_size_max must be >= 1, got {batch_size_max}'
            raise InvalidParameterError(message)

        self._batch_size_max = batch_size_max
        self._identity_field = identity_field

        self._models: dict[str, type[SyncableMixin]] = {
            model._meta.label: model
            for model in models
        }

        self._serializers: dict[str, SyncFieldSerializer] = {
            model._meta.label: SyncFieldSerializer(model)
            for model in models
        }

        self._upsert_strategy = upsert_strategy or StalenessGuardedUpsertStrategy(
            identity_field=identity_field,
        )

        self._many_to_many_applier = many_to_many_applier or ManyToManyApplier(
            identity_field=identity_field,
        )

        self._delete_strategies = delete_strategies or self._build_delete_strategies(models)

    def _build_delete_strategies(
        self,
        models: list[type[SyncableMixin]],
    ) -> dict[str, DeleteStrategy]:
        soft = SoftDeleteStrategy(identity_field=self._identity_field)
        hard = HardDeleteStrategy(identity_field=self._identity_field)

        return {
            model._meta.label: soft if self._has_field(model, 'is_deleted') else hard
            for model in models
        }

    def _check_batch_limit(self, count: int, operation: str) -> None:
        if count > self._batch_size_max:
            message = (
                f'{operation} received {count} items, '
                f'exceeds batch_size_max={self._batch_size_max}'
            )

            raise BatchLimitError(message)

    def _extract_field_data(
        self,
        sync_record: SyncRecord,
        many_to_many_names: set[str],
    ) -> dict[str, Any]:
        return {
            key: value
            for key, value in sync_record.data.items()
            if key not in many_to_many_names
        }

    def _extract_many_to_many_data(
        self,
        sync_record: SyncRecord,
        many_to_many_names: set[str],
    ) -> dict[str, list[Any]]:
        return {
            key: value
            for key, value in sync_record.data.items()
            if key in many_to_many_names
        }

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

    def delete_many(
        self,
        model_label: str,
        deletes: dict[str, int],
    ) -> None:
        if not deletes:
            return

        self._check_batch_limit(len(deletes), 'delete_many')

        model = self._get_model(model_label)
        strategy = self._delete_strategies[model_label]

        strategy.delete(model, deletes)

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
        serializer = self._serializers[model_label]

        skipped: set[str] = set()
        pending_many_to_many: dict[str, dict[str, list[Any]]] = {}

        with transaction.atomic():
            for key in sorted(records.keys()):
                sync_record = records[key]

                field_data = self._extract_field_data(sync_record, many_to_many_names)
                many_to_many_data = self._extract_many_to_many_data(sync_record, many_to_many_names)

                field_data = serializer.deserialize(field_data)

                applied = self._upsert_strategy.apply(model, key, sync_record, field_data)

                if not applied:
                    skipped.add(key)
                    continue

                if many_to_many_data:
                    pending_many_to_many[key] = many_to_many_data

            m2m_skipped = self._many_to_many_applier.apply(model, pending_many_to_many)
            skipped |= m2m_skipped

        return skipped
