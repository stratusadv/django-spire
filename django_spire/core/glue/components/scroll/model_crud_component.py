from __future__ import annotations

from abc import ABC
from typing import Any, ClassVar

from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django_glue import Glue

from django_spire.core.glue.components.confirmation import ModelDeleteConfirmationComponent
from django_spire.core.glue.components.form import ModelFormComponent  # noqa: TC001
from django_spire.core.glue.components.scroll.item_form_options import (
    ComponentItemFormOptions,
    PageItemFormOptions,
)
from django_spire.core.glue.components.scroll.queryset import QuerySetScrollComponent


class ModelCrudScrollComponent(QuerySetScrollComponent, ABC):
    """
    A :class:`QuerySetScrollComponent` with ready-made actions on its rows.
    The template's ``createItem()``, ``editItem(item)`` and ``deleteItem(item)``
    perform them, and each takes the item or its key.

    ``item_form_options`` says how a row is created and edited: a
    :class:`ComponentItemFormOptions` shows a form component in a modal, and
    a :class:`PageItemFormOptions` sends the user to a page. Left as ``None``,
    the list has no create or edit.

    ``delete_component`` is the confirmation shown before a row is deleted;
    confirming it soft-deletes the row. ``None`` turns deleting off.

    Only rows in ``get_queryset()`` can be edited or deleted. Each action is
    built from the scroll's own callables and row operations, so application
    code can replace any one of them or call them itself. A template that
    adds to the ``scroll_data`` block keeps these actions with
    ``{{ block.super }}``.
    """

    template = 'django_spire/glue/component/scroll/crud.html'
    delete_component: ClassVar[type[ModelDeleteConfirmationComponent] | None] = (
        ModelDeleteConfirmationComponent
    )
    item_form_options: ClassVar[ComponentItemFormOptions | PageItemFormOptions | None] = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if cls.item_form_options is not None and not isinstance(
            cls.item_form_options,
            ComponentItemFormOptions | PageItemFormOptions,
        ):
            message = (
                f'{cls.__name__}.item_form_options must be a ComponentItemFormOptions, a '
                'PageItemFormOptions, or None.'
            )
            raise ImproperlyConfigured(message)

    @Glue.attr(required_access=Glue.Access.DELETE)
    def delete_confirmation(self, pk: int) -> ModelDeleteConfirmationComponent:
        if self.delete_component is None:
            message = f'{type(self).__name__} does not allow its rows to be deleted.'
            raise PermissionDenied(message)

        return self.delete_component(
            model_obj=self.get_queryset().get(pk=pk),
            access=self.access,
        )

    @Glue.attr(required_access=Glue.Access.CHANGE)
    def item_form(self, pk: int | None = None) -> ModelFormComponent:
        if not isinstance(self.item_form_options, ComponentItemFormOptions):
            message = f'{type(self).__name__} has no form component to create or edit a row with.'
            raise PermissionDenied(message)

        if pk is not None:
            self.get_queryset().values_list('pk', flat=True).get(pk=pk)

        return self.item_form_options.build_component(pk=pk, access=self.access)
