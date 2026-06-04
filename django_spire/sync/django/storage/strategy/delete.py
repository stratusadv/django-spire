from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

from django_spire.sync.django.queryset import sync_bypass

if TYPE_CHECKING:
    from django_spire.sync.django.mixin import SyncableMixin


class DeleteStrategy(Protocol):
    def delete(
        self, model: type[SyncableMixin], deletes: dict[str, int], origin_node: str
    ) -> None: ...


def _record_tombstone(
    model_label: str, record_key: str, timestamp: int, sequence: int, origin_node: str
) -> None:
    from django_spire.sync.django.models.tombstone import SyncTombstone  # noqa: PLC0415

    SyncTombstone.objects.update_or_create(
        model_label=model_label,
        record_key=record_key,
        defaults={'origin_node': origin_node, 'sequence': sequence, 'timestamp': timestamp},
    )


class HardDeleteStrategy:
    def __init__(self, identity_field: str = 'id') -> None:
        self._identity_field = identity_field

    def delete(self, model: type[SyncableMixin], deletes: dict[str, int], origin_node: str) -> None:
        if not deletes:
            return

        from django_spire.sync.django.sequence import (  # noqa: PLC0415
            SyncSequenceAllocator,
        )

        keys = sorted(deletes.keys())
        sequence_first = SyncSequenceAllocator().allocate(len(keys)).value_first
        model_label = model._meta.label

        with sync_bypass():
            for index, key in enumerate(keys):
                tombstone_timestamp = deletes[key]

                staleness_filter = {
                    self._identity_field: key,
                    'sync_field_last_modified__lte': tombstone_timestamp,
                }

                model.objects.filter(**staleness_filter).delete()

                _record_tombstone(
                    model_label, key, tombstone_timestamp, sequence_first + index, origin_node
                )


class SoftDeleteStrategy:
    def __init__(self, identity_field: str = 'id') -> None:
        self._identity_field = identity_field

    def _collect_pending(
        self, instances: list[SyncableMixin], deletes: dict[str, int]
    ) -> list[SyncableMixin]:
        pending: list[SyncableMixin] = []

        for instance in instances:
            key = str(getattr(instance, self._identity_field))
            tombstone_timestamp = deletes[key]

            if instance.sync_field_last_modified > tombstone_timestamp:
                continue

            instance.is_deleted = True

            timestamps = dict(instance.sync_field_timestamps)
            timestamps['is_deleted'] = tombstone_timestamp
            instance.sync_field_timestamps = timestamps

            instance.sync_field_last_modified = max(
                instance.sync_field_last_modified, tombstone_timestamp
            )

            pending.append(instance)

        return pending

    def delete(self, model: type[SyncableMixin], deletes: dict[str, int], origin_node: str) -> None:
        if not deletes:
            return

        from django_spire.sync.django.sequence import (  # noqa: PLC0415
            SyncSequenceAllocator,
        )

        identity_lookup = {f'{self._identity_field}__in': list(deletes.keys())}
        instances = list(model.objects.filter(**identity_lookup))

        pending = self._collect_pending(instances, deletes)

        if not pending:
            return

        sequence_first = SyncSequenceAllocator().allocate(len(pending)).value_first
        model_label = model._meta.label

        with sync_bypass():
            for index, instance in enumerate(pending):
                key = str(getattr(instance, self._identity_field))
                tombstone_timestamp = deletes[key]
                local_sequence = sequence_first + index

                staleness_filter = {
                    self._identity_field: key,
                    'sync_field_last_modified__lte': tombstone_timestamp,
                }

                model.objects.filter(**staleness_filter).update(
                    is_deleted=True,
                    sync_field_last_modified=instance.sync_field_last_modified,
                    sync_field_origin_node=origin_node,
                    sync_field_sequence=local_sequence,
                    sync_field_timestamps=instance.sync_field_timestamps,
                )

                _record_tombstone(
                    model_label, key, tombstone_timestamp, local_sequence, origin_node
                )
