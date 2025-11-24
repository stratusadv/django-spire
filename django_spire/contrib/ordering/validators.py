from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.ordering.exceptions import OrderingMixinException

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet


class OrderingMixinValidator:
    def __init__(
        self,
        destination_objects: QuerySet[Model],
        position: int,
        obj: Model,
        origin_objects: QuerySet[Model],
    ):
        self._destination_objects = destination_objects
        self._position = position
        self._origin_objects = origin_objects
        self._obj = obj

        self._errors: list[OrderingMixinException] = []

    @property
    def errors(self) -> list[OrderingMixinException]:
        """Returns list of OrderingMixinException errors."""
        return self._errors

    def validate(self) -> bool:
        """
        Validates that the destination and origin and insertion objects and position are valid.
        Returns tuple of validity and applicable error messages.
        """

        self._validate_position()
        return not self._errors

    def _validate_position(self):
        """Ensure position is valid."""
        if self._position < 0 or not isinstance(self._position, int):
            self._errors.append(OrderingMixinException('Position must be a positive number.'))

        if self._position > len(self._destination_objects):
            self._errors.append(OrderingMixinException('Position must be less than the number of destination objects.'))
