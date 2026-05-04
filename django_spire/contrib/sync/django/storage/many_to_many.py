from __future__ import annotations

import logging

from typing import Any, TYPE_CHECKING

from django.db import IntegrityError

from django_spire.contrib.sync.django.queryset import sync_bypass

if TYPE_CHECKING:
    from django_spire.contrib.sync.django.mixin import SyncableMixin


logger = logging.getLogger(__name__)


class ManyToManyApplier:
    def __init__(self, identity_field: str = 'id') -> None:
        self._identity_field = identity_field

    def apply(
        self,
        model: type[SyncableMixin],
        pending: dict[str, dict[str, list[Any]]],
    ) -> set[str]:
        skipped: set[str] = set()

        if not pending:
            return skipped

        identity_lookup = {f'{self._identity_field}__in': list(pending.keys())}

        instances_by_key = {
            str(getattr(instance, self._identity_field)): instance
            for instance in model.objects.filter(**identity_lookup)
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
