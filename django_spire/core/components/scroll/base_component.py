from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any, ClassVar

from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django_glue import Glue
from django_glue.exceptions import GlueRequestError, GlueRequestErrorCode
from django_glue.response import GlueTemplateResponse

from django_spire.core.components.scroll.templates import template_extends

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django_glue.response import GlueResponse


SCROLL_TEMPLATES = frozenset({'django_spire/component/scroll/scroll.html'})
ITEM_TEMPLATES = frozenset({
    'django_spire/component/scroll/item/item.html',
    'django_spire/component/scroll/item/table_item.html',
})
BATCH_TEMPLATE = 'django_spire/component/scroll/scroll_batch.html'


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

    ``item_template`` is the markup for one item. Each item is rendered on
    the server, so the template must extend the scroll's ``item/item.html``
    or ``item/table_item.html``.

    A callable that changes an item fires ``item_added``, ``item_changed`` or
    ``item_removed`` with ``key=``, and the list updates that one row.
    """

    template = 'django_spire/component/scroll/scroll.html'
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
        """Return the item with this key, or ``None`` when it no longer belongs in the list."""

    @abstractmethod
    def get_item_key(self, item: Any) -> Any:
        """Return the value that identifies ``item`` among all items."""

    def introduce(self, request: HttpRequest) -> None:
        """Check, once per class, that its templates extend the scroll's own."""
        scroll_class = type(self)

        if scroll_class not in self._validated_classes:
            self._validate_templates()
            self._validated_classes.add(scroll_class)

        super().introduce(request)

    def _validate_templates(self) -> None:
        scroll_class = type(self)

        if not template_extends(scroll_class.template, SCROLL_TEMPLATES):
            message = (
                f'{scroll_class.__name__}.template {scroll_class.template!r} must extend '
                f'{min(SCROLL_TEMPLATES)!r}.'
            )
            raise ImproperlyConfigured(message)

        if scroll_class.item_template is None:
            if self.renders_items_on_server:
                message = (
                    f'{scroll_class.__name__} renders its items on the server, which needs '
                    'an item_template.'
                )
                raise ImproperlyConfigured(message)
        elif self.renders_items_on_server != template_extends(
            scroll_class.item_template,
            ITEM_TEMPLATES,
        ):
            message = (
                f'{scroll_class.__name__}.item_template {scroll_class.item_template!r} must '
                f'extend one of {sorted(ITEM_TEMPLATES)} when its rows are rendered on the '
                'server, and none of them when they are drawn in the browser.'
            )
            raise ImproperlyConfigured(message)

    @property
    def renders_items_on_server(self) -> bool:
        return True

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

    def _refuse_unless_rendered_on_server(self) -> None:
        if not self.renders_items_on_server:
            message = f'{type(self).__name__} sends its rows as Glue items, not as HTML.'
            raise PermissionDenied(message)

    def _validate_offset(self, offset: int) -> None:
        if offset < 0:
            raise GlueRequestError(
                code=GlueRequestErrorCode.INVALID_KWARGS,
                message='offset must not be negative.',
                details={'offset': offset},
            )

    @Glue.attr(skip_rerender=True)
    def load_items(self, request: HttpRequest, offset: int) -> GlueResponse:
        self._refuse_unless_rendered_on_server()
        self._validate_offset(offset)

        return GlueTemplateResponse(
            request,
            BATCH_TEMPLATE,
            {
                'batch': self._get_batch(offset),
                'component': self,
            },
        )

    @Glue.attr(skip_rerender=True)
    def load_item(self, request: HttpRequest, key: int | str) -> GlueResponse | None:
        self._refuse_unless_rendered_on_server()

        item = self.get_item(key)

        if item is None:
            return None

        return GlueTemplateResponse(
            request,
            self.item_template,
            {
                'item': item,
                'item_key': self.get_item_key(item),
                'component': self,
            },
        )
