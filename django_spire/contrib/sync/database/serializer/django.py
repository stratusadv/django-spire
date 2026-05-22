from __future__ import annotations

import uuid

from typing import Any

from django_spire.contrib.sync.core.exceptions import UnknownModelError
from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.database.serializer.base import Serializer


class DjangoModelSerializer(Serializer):
    def __init__(
        self,
        models: list[type],
        identity_field: str = 'id',
    ) -> None:
        self._identity_field = identity_field
        self._models = {model._meta.label: model for model in models}

    def _coerce_value(self, value: Any) -> Any:
        if isinstance(value, uuid.UUID):
            return str(value)

        return value

    def _get_many_to_many_names(self, model: type) -> list[str]:
        return [field.name for field in model._meta.many_to_many]

    def _resolve_model(self, model_label: str) -> type:
        model = self._models.get(model_label)

        if model is None:
            message = f'Unknown syncable model: {model_label!r}'
            raise UnknownModelError(message)

        return model

    def deserialize(
        self,
        model_label: str,
        record: SyncRecord,
    ) -> Any:
        model = self._resolve_model(model_label)
        many_to_many_names = set(self._get_many_to_many_names(model))

        field_data = {
            key: value for key, value in record.data.items()
            if key not in many_to_many_names
        }

        instance = model(**field_data)
        instance.sync_field_timestamps = record.timestamps

        return instance

    def get_identity(self, instance: Any) -> str:
        value = getattr(instance, self._identity_field)
        return str(value)

    def serialize(self, instance: Any) -> SyncRecord:
        data: dict[str, Any] = {}

        for field in instance._meta.concrete_fields:
            value = getattr(instance, field.attname)
            data[field.name] = self._coerce_value(value)

        for field in instance._meta.many_to_many:
            related = getattr(instance, field.name)

            data[field.name] = sorted(
                str(primary_key)
                for primary_key in related.values_list('pk', flat=True)
            )

        key = str(getattr(instance, self._identity_field))
        timestamps = dict(getattr(instance, 'sync_field_timestamps', {}))

        return SyncRecord(key=key, data=data, timestamps=timestamps)
