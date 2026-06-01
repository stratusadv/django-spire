from __future__ import annotations

import json
import logging

from typing import Any, TYPE_CHECKING

from django.db.models import Q

from django_spire.sync.core import UnknownModelError
from django_spire.sync.database.record import SyncRecord
from django_spire.sync.django.serializer import SyncFieldSerializer

if TYPE_CHECKING:
    from django_spire.sync.django.mixin import SyncableMixin


logger = logging.getLogger(__name__)


def _coerce_timestamp_value(
    value: Any,
    label: str,
    key: str,
    timestamp_key: str,
) -> int | None:
    if isinstance(value, bool):
        logger.warning(
            'Boolean sync_field_timestamps value for %s key=%s field=%s',
            label,
            key,
            timestamp_key,
        )

        return None

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    logger.warning(
        'Non-numeric sync_field_timestamps value for %s key=%s field=%s: %r',
        label,
        key,
        timestamp_key,
        value,
    )

    return None


def _coerce_timestamps(
    raw: Any,
    label: str,
    key: str,
) -> dict[str, int]:
    if raw is None or raw == '':
        return {}

    if isinstance(raw, (bytes, bytearray)):
        try:
            raw = raw.decode('utf-8')
        except UnicodeDecodeError:
            logger.warning(
                'Undecodable sync_field_timestamps for %s key=%s',
                label,
                key,
            )

            return {}

    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(
                'Invalid sync_field_timestamps JSON for %s key=%s: %r',
                label,
                key,
                raw,
            )

            return {}

    if not isinstance(raw, dict):
        logger.warning(
            'Unexpected sync_field_timestamps type %s for %s key=%s',
            type(raw).__name__,
            label,
            key,
        )

        return {}

    result: dict[str, int] = {}

    for timestamp_key, timestamp_value in raw.items():
        if not isinstance(timestamp_key, str):
            logger.warning(
                'Non-string sync_field_timestamps key for %s key=%s: %r',
                label,
                key,
                timestamp_key,
            )

            continue

        coerced = _coerce_timestamp_value(timestamp_value, label, key, timestamp_key)

        if coerced is None:
            continue

        if coerced < 0:
            logger.warning(
                'Negative sync_field_timestamps value for %s key=%s field=%s: %d',
                label,
                key,
                timestamp_key,
                coerced,
            )

            continue

        result[timestamp_key] = coerced

    return result


class DjangoRecordReader:
    def __init__(
        self,
        models: list[type[SyncableMixin]],
        identity_field: str = 'id',
    ) -> None:
        self._identity_field = identity_field

        self._models: dict[str, type[SyncableMixin]] = {
            model._meta.label: model
            for model in models
        }

        self._serializers: dict[str, SyncFieldSerializer] = {
            model._meta.label: SyncFieldSerializer(model)
            for model in models
        }

    def _get_many_to_many_names(self, model: type[SyncableMixin]) -> set[str]:
        return {field.name for field in model._meta.many_to_many}

    def _get_model(self, model_label: str) -> type[SyncableMixin]:
        model = self._models.get(model_label)

        if model is None:
            message = f'Unknown syncable model: {model_label!r}'
            raise UnknownModelError(message)

        return model

    def _instance_to_record(self, instance: SyncableMixin) -> SyncRecord:
        label = instance._meta.label
        key = str(getattr(instance, self._identity_field))

        serializer = self._serializers[label]
        data = serializer.serialize(instance)

        for field in instance._meta.many_to_many:
            related = getattr(instance, field.name)

            data[field.name] = sorted(
                str(related_instance.pk)
                for related_instance in related.all()
            )

        timestamps = _coerce_timestamps(
            instance.sync_field_timestamps,
            label,
            key,
        )

        origin = instance.sync_field_origin_node or ''

        if not isinstance(origin, str):
            origin = ''

        modified_last = instance.sync_field_last_modified

        if isinstance(modified_last, float):
            modified_last = int(modified_last)
        elif not isinstance(modified_last, int):
            modified_last = 0

        sequence = instance.sync_field_sequence

        if isinstance(sequence, float):
            sequence = int(sequence)
        elif not isinstance(sequence, int):
            sequence = 0

        if not timestamps and modified_last == 0:
            logger.error(
                'Reading ghost record from database: %s key=%s '
                '(sync_field_last_modified=0, sync_field_timestamps=empty). '
                'stamp_unstamped_records should prevent this; '
                'check that AppConfig.ready() runs and the storage layer '
                'has access to a configured clock.',
                label,
                key,
            )

        return SyncRecord(
            key=key,
            data=data,
            timestamps=timestamps,
            sequence=sequence,
            origin_node=origin,
            received_at=modified_last,
        )

    def get_changed_since(
        self,
        model_label: str,
        sequence: int,
        peer_node_id: str,
        sequence_max: int | None = None,
        limit: int | None = None,
        after_key: str | None = None,
    ) -> dict[str, SyncRecord]:
        model = self._get_model(model_label)
        many_to_many_names = self._get_many_to_many_names(model)

        if after_key:
            identity_gt = {
                f'{self._identity_field}__gt': after_key,
            }

            queryset = model.objects.filter(
                Q(sync_field_sequence__gt=sequence) |
                Q(
                    sync_field_sequence=sequence,
                    **identity_gt,
                ),
            )
        else:
            queryset = model.objects.filter(
                sync_field_sequence__gt=sequence,
            )

        if sequence_max is not None:
            queryset = queryset.filter(
                sync_field_sequence__lte=sequence_max,
            )

        if peer_node_id:
            queryset = queryset.exclude(
                sync_field_origin_node=peer_node_id,
            )

        queryset = queryset.order_by(
            'sync_field_sequence',
            self._identity_field,
        )

        if limit is not None:
            queryset = queryset[:limit]

        if many_to_many_names:
            queryset = queryset.prefetch_related(
                *many_to_many_names,
            )

        return {
            str(getattr(instance, self._identity_field)): self._instance_to_record(instance)
            for instance in queryset
        }

    def get_deletes_since(
        self,
        model_label: str,
        sequence: int,
        peer_node_id: str,
        sequence_max: int | None = None,
    ) -> dict[str, int]:
        from django_spire.sync.django.models.tombstone import SyncTombstone  # noqa: PLC0415

        queryset = SyncTombstone.objects.filter(
            model_label=model_label,
            sequence__gt=sequence,
        )

        if sequence_max is not None:
            queryset = queryset.filter(sequence__lte=sequence_max)

        if peer_node_id:
            queryset = queryset.exclude(origin_node=peer_node_id)

        rows = queryset.values_list('record_key', 'timestamp')

        return dict(rows)

    def get_records(
        self,
        model_label: str,
        keys: set[str],
    ) -> dict[str, SyncRecord]:
        if not keys:
            return {}

        model = self._get_model(model_label)
        many_to_many_names = self._get_many_to_many_names(model)

        identity_lookup = {f'{self._identity_field}__in': keys}
        queryset = model.objects.filter(**identity_lookup)

        if many_to_many_names:
            queryset = queryset.prefetch_related(*many_to_many_names)

        return {
            str(getattr(instance, self._identity_field)): self._instance_to_record(instance)
            for instance in queryset
        }

    def get_syncable_models(self) -> list[str]:
        return sorted(self._models.keys())

    def get_tombstones(
        self,
        model_label: str,
        keys: set[str],
    ) -> dict[str, int]:
        if not keys:
            return {}

        from django_spire.sync.django.models.tombstone import SyncTombstone  # noqa: PLC0415

        rows = (
            SyncTombstone.objects
            .filter(model_label=model_label, record_key__in=keys)
            .values_list('record_key', 'timestamp')
        )

        return dict(rows)
