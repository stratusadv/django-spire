from __future__ import annotations

from typing import Any

from django.core.exceptions import ImproperlyConfigured
from django_glue import Glue
from django_glue.glue.base import BaseGlue  # noqa: TC002
from django_glue.glue.sequence import SequenceGlue

ITEM_NAME_PREFIX = 'item_'


class GlueScrollItemsMixin:
    """
    Sends each item of a scroll to the browser as a Glue object.

    Listed ahead of a :class:`BaseScrollComponent` subclass, it replaces plain
    data items with whatever ``get_glue_item(item, name)`` returns, so the row
    markup can call the object's Glue methods. That hook must build its Glue
    object with ``name`` as its unique name, which carries the item's key.

    The items never arrive with the render: a Glue child is not derived again
    when its component refreshes, so every batch comes from ``load_items()``.
    A batch holds up to ``batch_size`` items, and a full one means there may
    be more.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if getattr(cls, 'item_template', None) is not None:
            message = (
                f'{cls.__name__} uses GlueScrollItemsMixin with an item_template: rows '
                'rendered on the server have no item in the browser to be a Glue object.'
            )
            raise ImproperlyConfigured(message)

    def _get_named_glue_item(self, item: Any) -> BaseGlue:
        return self.get_glue_item(item, f'{ITEM_NAME_PREFIX}{self.get_item_key(item)}')

    @Glue.property
    def first_batch_data(self) -> None:
        return None

    @Glue.attr
    def load_item(self, key: int | str) -> BaseGlue | None:
        item = self.get_item(key)

        if item is None:
            return None

        return self._get_named_glue_item(item)

    @Glue.attr
    def load_items(self, offset: int) -> SequenceGlue:
        self._validate_offset(offset)

        return SequenceGlue(
            [self._get_named_glue_item(item) for item in self.get_items(offset, self.batch_size)],
            name=f'batch_{offset}',
            access=self.access,
        )
