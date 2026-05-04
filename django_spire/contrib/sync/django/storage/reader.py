from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Q

from django_spire.contrib.sync.core.exceptions import UnknownModelError
from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.django.serializer import SyncFieldSerializer

if TYPE_CHECKING:
    from django_spire.contrib.sync.django.mixin import SyncableMixin


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
        serializer = self._serializers[instance._meta.label]
        data = serializer.serialize(instance)

        for field in instance._meta.many_to_many:
            related = getattr(instance, field.name)

            data[field.name] = sorted(
                str(related_instance.pk)
                for related_instance in related.all()
            )

        return SyncRecord(
            key=str(getattr(instance, self._identity_field)),
            data=data,
            timestamps=dict(instance.sync_field_timestamps),
            received_at=instance.sync_field_last_modified,
        )

    def get_changed_since(
        self,
        model_label: str,
        timestamp: int,
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
                Q(sync_field_last_modified__gt=timestamp) |
                Q(
                    sync_field_last_modified=timestamp,
                    **identity_gt,
                ),
            )
        else:
            queryset = model.objects.filter(
                sync_field_last_modified__gt=timestamp,
            )

        queryset = queryset.order_by(
            'sync_field_last_modified',
            self._identity_field,
        )

        if limit is not None:
            queryset = queryset[:limit]

        if many_to_many_names:
            queryset = queryset.prefetch_related(
                *many_to_many_names
            )

        return {
            str(getattr(instance, self._identity_field)): self._instance_to_record(instance)
            for instance in queryset
        }

    def get_deletes_since(
        self,
        model_label: str,
        timestamp: int,
    ) -> dict[str, int]:
        from django_spire.contrib.sync.django.models.tombstone import SyncTombstone  # noqa: PLC0415

        rows = (
            SyncTombstone.objects
            .filter(model_label=model_label, timestamp__gt=timestamp)
            .values_list('record_key', 'timestamp')
        )

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
