from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

from django_spire.contrib.sync.django.queryset import sync_bypass

if TYPE_CHECKING:
    from django_spire.contrib.sync.django.mixin import SyncableMixin


class DeleteStrategy(Protocol):
    def delete(self, model: type[SyncableMixin], deletes: dict[str, int]) -> None: ...


class HardDeleteStrategy:
    def __init__(self, identity_field: str = 'id') -> None:
        self._identity_field = identity_field

    def delete(
        self,
        model: type[SyncableMixin],
        deletes: dict[str, int],
    ) -> None:
        for key, tombstone_ts in deletes.items():
            staleness_filter = {
                self._identity_field: key,
                'sync_field_last_modified__lte': tombstone_ts,
            }

            model.objects.filter(**staleness_filter).delete()


class SoftDeleteStrategy:
    def __init__(self, identity_field: str = 'id') -> None:
        self._identity_field = identity_field

    def _collect_pending(
        self,
        instances: list[SyncableMixin],
        deletes: dict[str, int],
    ) -> list[SyncableMixin]:
        pending: list[SyncableMixin] = []

        for instance in instances:
            key = str(getattr(instance, self._identity_field))
            tombstone_ts = deletes[key]

            if instance.sync_field_last_modified > tombstone_ts:
                continue

            instance.is_deleted = True

            timestamps = dict(instance.sync_field_timestamps)
            timestamps['is_deleted'] = tombstone_ts
            instance.sync_field_timestamps = timestamps

            instance.sync_field_last_modified = max(
                instance.sync_field_last_modified,
                tombstone_ts,
            )

            pending.append(instance)

        return pending

    def delete(
        self,
        model: type[SyncableMixin],
        deletes: dict[str, int],
    ) -> None:
        identity_lookup = {f'{self._identity_field}__in': list(deletes.keys())}
        instances = list(model.objects.filter(**identity_lookup))

        pending = self._collect_pending(instances, deletes)

        if not pending:
            return

        with sync_bypass():
            for instance in pending:
                key = str(getattr(instance, self._identity_field))
                tombstone_ts = deletes[key]

                staleness_filter = {
                    self._identity_field: key,
                    'sync_field_last_modified__lte': tombstone_ts,
                }

                model.objects.filter(**staleness_filter).update(
                    is_deleted=True,
                    sync_field_timestamps=instance.sync_field_timestamps,
                    sync_field_last_modified=instance.sync_field_last_modified,
                )
