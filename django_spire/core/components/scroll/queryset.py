from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from django.core.exceptions import ImproperlyConfigured, PermissionDenied, ValidationError
from django_glue import Glue
from django_glue.exceptions import GlueModelInstanceNotFoundError

from django_spire.core.components.scroll.base import BaseScrollComponent

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet

ITEM_NAME_PREFIX = 'item_'


class QuerySetScrollComponent(BaseScrollComponent, ABC):
    """
    A :class:`BaseScrollComponent` whose items are the rows of a queryset.

    Subclasses return the rows from ``get_queryset()``. The primary key
    identifies each row and is appended to the queryset's ordering, so that
    the order is total; a queryset with no ordering is listed by primary key.
    Each item is a model instance.

    ``glue_items`` sends each row to the browser as the Glue model
    ``get_glue_item()`` builds, in place of rendering it on the server, so
    the row markup can call the model's Glue methods. The rows are drawn in
    the browser: ``item_template`` is Alpine markup that reads ``item``, drawn
    by the ``scroll_item`` block of the component template, which a list may
    fill in itself instead. The browser then loads rows with
    ``load_glue_items()`` and ``load_glue_item()``, and the other loads are
    refused.

    Glue rows never arrive with the render: a Glue child is not derived again
    when its component refreshes, so every batch comes from
    ``load_glue_items()``. A batch holds up to ``batch_size`` rows, and a full
    one means there may be more.
    """

    glue_items: ClassVar[bool] = False

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if cls.glue_items and cls.get_glue_item is QuerySetScrollComponent.get_glue_item:
            message = (
                f'{cls.__name__} sends Glue items, which needs get_glue_item(): override it '
                "to build each row's Glue model."
            )
            raise ImproperlyConfigured(message)

    @abstractmethod
    def get_queryset(self) -> QuerySet:
        """Return the rows this scroll lists, in the order it lists them."""

    @property
    def renders_items_on_server(self) -> bool:
        return not self.glue_items

    def get_items(self, offset: int, limit: int) -> list[Model]:
        queryset = self.get_queryset()
        ordering = queryset.query.order_by or queryset.model._meta.ordering

        return list(queryset.order_by(*ordering, 'pk')[offset:offset + limit])

    def get_item(self, key: Any) -> Model | None:
        try:
            return self.get_queryset().filter(pk=key).first()
        except (TypeError, ValueError, ValidationError):
            return None

    def get_item_key(self, item: Model) -> Any:
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

    def get_glue_item(self, item: Model, name: str) -> Glue.Model:
        """
        Return the Glue model the browser receives for ``item`` when
        ``glue_items`` is set, built with ``name`` as its unique name and with
        exactly the fields, access and form the row needs. A list that sets
        ``glue_items`` must override it.

        To edit a row in place, pass the row a ``form``, bind the row's inputs
        to ``item.form``, and save with the form's own method, such as
        ``item.form.save_model_obj()``. That runs the form's validation and
        whatever the application's save does. ``item.save()`` writes the model
        directly instead.
        """
        raise NotImplementedError

    def _get_named_glue_item(self, item: Model) -> Glue.Model:
        return self.get_glue_item(item, f'{ITEM_NAME_PREFIX}{self.get_item_key(item)}')

    def _refuse_unless_glue_items(self) -> None:
        if not self.glue_items:
            message = f'{type(self).__name__} renders its rows on the server, not as Glue items.'
            raise PermissionDenied(message)

    @Glue.attr
    def load_glue_item(self, key: int | str) -> Glue.Model | None:
        self._refuse_unless_glue_items()

        item = self.get_item(key)

        if item is None:
            return None

        return self._get_named_glue_item(item)

    @Glue.attr
    def load_glue_items(self, offset: int) -> Glue.Sequence:
        self._refuse_unless_glue_items()
        self._validate_offset(offset)

        return Glue.Sequence(
            [self._get_named_glue_item(item) for item in self.get_items(offset, self.batch_size)],
            name=f'batch_{offset}',
            access=self.access,
        )
