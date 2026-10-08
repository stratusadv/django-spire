from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence  # noqa: TC003
from typing import TYPE_CHECKING, Any, ClassVar

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django_glue import Glue

from django_spire.core.glue.components.scroll.base import BaseScrollComponent
from django_spire.core.glue.components.scroll.glue_items import GlueScrollItemsMixin

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet
    from django_glue.glue.objects.django.model.object import ModelGlue


class QuerySetScrollComponent(BaseScrollComponent, ABC):
    """
    A :class:`BaseScrollComponent` whose items are the rows of a queryset.

    Subclasses return the rows from ``get_queryset()``, which must be
    ordered; the primary key is appended to the ordering so that it is total,
    and identifies each row. With ``item_template`` set the items are model
    instances. Left unset they are dicts of ``pk`` and ``fields``.

    Behind :class:`GlueScrollItemsMixin`, each row reaches the browser as a
    Glue model of ``fields``, built by ``get_glue_item()``.
    """

    fields: ClassVar[Sequence[str]] = ()

    @abstractmethod
    def get_queryset(self) -> QuerySet:
        """Return the ordered rows this scroll lists."""

    @property
    def _sends_dicts(self) -> bool:
        return self.item_template is None and not isinstance(self, GlueScrollItemsMixin)

    def _as_items(self, queryset: QuerySet) -> QuerySet:
        if self._sends_dicts:
            return queryset.values('pk', *self.fields)

        return queryset

    def get_glue_item(self, item: Model, name: str, **kwargs: Any) -> ModelGlue:
        """
        Return the Glue model the browser receives for ``item``. An override
        passes further ``Glue.model`` options through ``super()``.
        """
        options = {'access': self.access, 'fields': self.fields, **kwargs}

        if not options['fields'] and not options.get('exclude'):
            message = (
                f'{type(self).__name__} sends its rows as Glue models, which need to know '
                'what to expose: set fields on the class.'
            )
            raise ImproperlyConfigured(message)

        return Glue.model(target=item, unique_name=name, **options)

    def get_items(self, offset: int, limit: int) -> list[Model | dict[str, Any]]:
        queryset = self.get_queryset()

        if not queryset.ordered:
            message = (
                f'{type(self).__name__}.get_queryset() must return an ordered queryset: '
                'unordered rows can repeat or go missing between batches.'
            )
            raise ImproperlyConfigured(message)

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
