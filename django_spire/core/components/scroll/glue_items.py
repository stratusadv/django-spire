from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.core.exceptions import ImproperlyConfigured
from django_glue import Glue

from django_spire.core.components.scroll.base import ScrollItemRenderMode
from django_spire.core.components.scroll.queryset import QuerySetScrollComponent

if TYPE_CHECKING:
    from django.db.models import Model

ITEM_NAME_PREFIX = 'item_'


class GlueScrollItemsMixin:
    """
    Sends each row of a queryset scroll to the browser as a Glue model.

    Listed ahead of a :class:`QuerySetScrollComponent` subclass, it replaces
    dict rows with the Glue model ``get_glue_item(item, name)`` builds from
    ``fields``, so the row markup can call the model's Glue methods. The rows
    are drawn in the browser, so the list's ``item_render_mode`` must be
    ``CLIENT``.

    To edit a row in place, override ``get_glue_item()`` to pass the row a
    ``form``, bind the row's inputs to ``item.form``, and save with the form's
    own method, such as ``item.form.save_model_obj()``. That runs the form's
    validation and whatever the application's save does. ``item.save()``
    writes the model directly instead.

    The items never arrive with the render: a Glue child is not derived again
    when its component refreshes, so every batch comes from ``load_items()``.
    A batch holds up to ``batch_size`` items, and a full one means there may
    be more.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if not issubclass(cls, QuerySetScrollComponent):
            message = (
                f'{cls.__name__} uses GlueScrollItemsMixin without a QuerySetScrollComponent: '
                'list the mixin ahead of one, since it builds each row from a model instance.'
            )
            raise ImproperlyConfigured(message)

        if cls.item_render_mode is ScrollItemRenderMode.SERVER:
            message = (
                f'{cls.__name__} uses GlueScrollItemsMixin with item_render_mode SERVER: '
                'rows rendered on the server have no item in the browser to be a Glue object.'
            )
            raise ImproperlyConfigured(message)

    @property
    def _sends_dicts(self) -> bool:
        return False

    def get_glue_item(self, item: Model, name: str, **kwargs: Any) -> Glue.Model:
        """
        Return the Glue model the browser receives for ``item``, built with
        ``name`` as its unique name. An override passes further ``Glue.model``
        options through ``super()``.
        """
        options = {'access': self.access, 'fields': self.fields, **kwargs}

        if not options['fields'] and not options.get('exclude'):
            message = (
                f'{type(self).__name__} sends its rows as Glue models, which need to know '
                'what to expose: set fields on the class.'
            )
            raise ImproperlyConfigured(message)

        return Glue.model(target=item, unique_name=name, **options)

    def _get_named_glue_item(self, item: Model) -> Glue.Model:
        return self.get_glue_item(item, f'{ITEM_NAME_PREFIX}{self.get_item_key(item)}')

    @Glue.property
    def first_batch_data(self) -> None:
        return None

    @Glue.attr
    def load_item(self, key: int | str) -> Glue.Model | None:
        item = self.get_item(key)

        if item is None:
            return None

        return self._get_named_glue_item(item)

    @Glue.attr
    def load_items(self, offset: int) -> Glue.Sequence:
        self._validate_offset(offset)

        return Glue.Sequence(
            [self._get_named_glue_item(item) for item in self.get_items(offset, self.batch_size)],
            name=f'batch_{offset}',
            access=self.access,
        )
