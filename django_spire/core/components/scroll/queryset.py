from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence  # noqa: TC003
from typing import TYPE_CHECKING, Any, ClassVar

from django.core.exceptions import ValidationError
from django_glue.exceptions import GlueModelInstanceNotFoundError

from django_spire.core.components.scroll.base import BaseScrollComponent

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet


class QuerySetScrollComponent(BaseScrollComponent, ABC):
    """
    A :class:`BaseScrollComponent` whose items are the rows of a queryset.

    Subclasses return the rows from ``get_queryset()``. The primary key
    identifies each row and is appended to the queryset's ordering, so that
    the order is total; a queryset with no ordering is listed by primary key.

    Items rendered on the server are model instances. Items rendered in the
    browser are dicts of ``pk`` and ``fields``.
    """

    fields: ClassVar[Sequence[str]] = ()

    @abstractmethod
    def get_queryset(self) -> QuerySet:
        """Return the rows this scroll lists, in the order it lists them."""

    @property
    def _sends_dicts(self) -> bool:
        return not self.renders_items_on_server

    def _as_items(self, queryset: QuerySet) -> QuerySet:
        if self._sends_dicts:
            return queryset.values('pk', *self.fields)

        return queryset

    def get_items(self, offset: int, limit: int) -> list[Model | dict[str, Any]]:
        queryset = self.get_queryset()
        ordering = queryset.query.order_by or queryset.model._meta.ordering

        return list(self._as_items(queryset.order_by(*ordering, 'pk'))[offset:offset + limit])

    def get_item(self, key: Any) -> Model | dict[str, Any] | None:
        try:
            return self._as_items(self.get_queryset().filter(pk=key)).first()
        except (TypeError, ValueError, ValidationError):
            return None

    def get_item_key(self, item: Model | dict[str, Any]) -> Any:
        if self._sends_dicts:
            return item['pk']

        return item.pk

    def get_instance(self, pk: Any) -> Model:
        """
        Return the row of ``get_queryset()`` with this primary key, for a
        callable that acts on one row. A row that is not in the list is
        reported as Glue's ``model_instance_not_found``, a 404.
        """
        queryset = self.get_queryset()

        try:
            return queryset.get(pk=pk)
        except queryset.model.DoesNotExist as error:
            raise GlueModelInstanceNotFoundError(queryset.model._meta.label, pk) from error
