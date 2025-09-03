from __future__ import annotations


from typing_extensions import TYPE_CHECKING

from django.db.models import QuerySet

from django_spire.contrib.ordering.exceptions import OrderingMixinException

if TYPE_CHECKING:
    from typing import Callable
    from django.db.models import Model


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
        self._run_check(self._validate_position)

        return False if self._errors else True

    def _run_check(self, func: Callable):
        """Stores errors found during validation and proceeds"""
        try:
            func()
        except OrderingMixinException as e:
            self._errors.append(e)

    def _validate_position(self):
        """Ensure position is valid."""
        if self._position < 0 or not isinstance(self._position, int):
            raise OrderingMixinException('Position must be a positive number.')

        if self._position > len(self._destination_objects):
            raise OrderingMixinException('Position must be less than the number of destination objects.')
