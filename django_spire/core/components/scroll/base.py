from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any, ClassVar

from django.core.exceptions import ImproperlyConfigured
from django_glue import Glue
from django_glue.exceptions import GlueRequestError, GlueRequestErrorCode
from django_glue.response import GlueTemplateResponse

from django_spire.core.components.scroll.templates import template_extends

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django_glue.response import GlueResponse


SCROLL_TEMPLATES = frozenset({'django_spire/component/scroll/base.html'})
ITEM_TEMPLATES = frozenset({
    'django_spire/component/scroll/item.html',
    'django_spire/component/scroll/table_row.html',
})
BATCH_TEMPLATE = 'django_spire/component/scroll/batch.html'


@dataclass(frozen=True)
class ScrollBatch:
    items: list[Any]
    keys: list[Any]
    has_more: bool

    @property
    def rows(self) -> list[tuple[Any, Any]]:
        return list(zip(self.keys, self.items, strict=True))


class BaseScrollComponent(Glue.Component, ABC):
    """
    An infinite list of any kind of item.

    Subclasses supply the items through ``get_items()``, ``get_item()`` and
    ``get_item_key()``; this base owns paging and every client behaviour.
    The server keeps no position: the client sends the number of items it
    holds, and a render always shows the first batch.

    With ``item_template`` set, each item is rendered on the server through
    that template, which must extend the scroll's ``item.html`` or
    ``table_row.html``. Left unset, items are sent as data and rendered by
    the ``scroll_item`` block of the component template.

    A callable that changes an item fires ``item_added``, ``item_changed`` or
    ``item_removed`` with ``key=``, and the list updates that one row.
    """

    template = 'django_spire/component/scroll/base.html'
    item_template: ClassVar[str | None] = None
    batch_size: ClassVar[int] = 25

    item_added = Glue.event()
    item_changed = Glue.event()
    item_removed = Glue.event()

    _validated_classes: ClassVar[set[type]] = set()

    @abstractmethod
    def get_items(self, offset: int, limit: int) -> list[Any]:
        """
        Return up to ``limit`` items starting at ``offset``, in an order that
        is the same on every call.
        """

    @abstractmethod
    def get_item(self, key: Any) -> Any | None:
        """
        Return the item with this key, or ``None`` when it no longer belongs
        in the list.
        """

    @abstractmethod
    def get_item_key(self, item: Any) -> Any:
        """Return the value that identifies ``item`` among all items."""

    def introduce(self, request: HttpRequest) -> None:
        self._base_post_init_ran = False
        super().introduce(request)

        if not self._base_post_init_ran:
            message = (
                f'{type(self).__name__}.__post_init__() must call '
                'super().__post_init__(request).'
            )
            raise ImproperlyConfigured(message)

    def __post_init__(self, request: HttpRequest) -> None:
        """
        Check, once per class, that its templates extend the scroll's own. A
        subclass that overrides this must call ``super().__post_init__(request)``.
        """
        self._base_post_init_ran = True
        scroll_class = type(self)

        if scroll_class in self._validated_classes:
            return

        if not template_extends(scroll_class.template, SCROLL_TEMPLATES):
            message = (
                f'{scroll_class.__name__}.template {scroll_class.template!r} must extend '
                f'{min(SCROLL_TEMPLATES)!r}.'
            )
            raise ImproperlyConfigured(message)

        if scroll_class.item_template is not None and not template_extends(
            scroll_class.item_template,
            ITEM_TEMPLATES,
        ):
            message = (
                f'{scroll_class.__name__}.item_template {scroll_class.item_template!r} must '
                f'extend one of {sorted(ITEM_TEMPLATES)}.'
            )
            raise ImproperlyConfigured(message)

        self._validated_classes.add(scroll_class)

    def _get_batch(self, offset: int) -> ScrollBatch:
        items = self.get_items(offset, self.batch_size + 1)
        batch_items = items[:self.batch_size]

        return ScrollBatch(
            items=batch_items,
            keys=[self.get_item_key(item) for item in batch_items],
            has_more=len(items) > self.batch_size,
        )

    @cached_property
    def first_batch(self) -> ScrollBatch:
        return self._get_batch(0)

    @Glue.property
    def first_batch_data(self) -> dict[str, Any] | None:
        if self.item_template is not None:
            return None

        return {
            'items': self.first_batch.items,
            'keys': self.first_batch.keys,
            'has_more': self.first_batch.has_more,
        }

    def _validate_offset(self, offset: int) -> None:
        if offset < 0:
            raise GlueRequestError(
                code=GlueRequestErrorCode.INVALID_KWARGS,
                message='offset must not be negative.',
                details={'offset': offset},
            )

    @Glue.attr(skip_rerender=True)
    def load_items(self, request: HttpRequest, offset: int) -> GlueResponse | dict[str, Any]:
        self._validate_offset(offset)

        batch = self._get_batch(offset)

        if self.item_template is None:
            return {
                'items': batch.items,
                'keys': batch.keys,
                'has_more': batch.has_more,
            }

        return GlueTemplateResponse(
            request,
            BATCH_TEMPLATE,
            {
                'batch': batch,
                'component': self,
            },
        )

    @Glue.attr(skip_rerender=True)
    def load_item(
        self,
        request: HttpRequest,
        key: int | str,
    ) -> GlueResponse | dict[str, Any] | None:
        item = self.get_item(key)

        if item is None:
            return None

        if self.item_template is None:
            return {
                'item': item,
                'key': self.get_item_key(item),
            }

        return GlueTemplateResponse(
            request,
            self.item_template,
            {
                'item': item,
                'item_key': self.get_item_key(item),
                'component': self,
            },
        )
