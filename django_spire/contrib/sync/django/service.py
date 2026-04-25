from __future__ import annotations

from typing import Any, TYPE_CHECKING

from django_spire.contrib.sync.core.exceptions import InvalidParameterError

if TYPE_CHECKING:
    from django_spire.contrib.sync.django.mixin import SyncableMixin


class SyncableModelService:
    @staticmethod
    def set_m2m(
        instance: SyncableMixin,
        field_name: str,
        values: list[Any],
    ) -> None:
        if instance._state.adding:
            message = (
                f'Cannot set M2M field {field_name!r} before the '
                f'instance is saved. Call save() first.'
            )

            raise InvalidParameterError(message)

        getattr(instance, field_name).set(values)
