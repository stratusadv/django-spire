from __future__ import annotations

from abc import ABC
from typing import Any, ClassVar

from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django_glue import Glue

from django_spire.core.components.confirmation import BaseModelDeleteConfirmationComponent
from django_spire.core.components.confirmation import options as delete_options
from django_spire.core.components.form import ModelFormComponent
from django_spire.core.components.form import options as form_options
from django_spire.core.components.scroll.queryset import QuerySetScrollComponent


class ModelCrudScrollComponent(QuerySetScrollComponent, ABC):
    """
    A :class:`QuerySetScrollComponent` with ready-made actions on its rows.
    The template's ``createItem()``, ``editItem(item)`` and ``deleteItem(item)``
    perform them, and each takes the item or its key.

    ``item_form_options`` says how a row is created and edited: a
    ``ModelCrudScrollComponent.FormOptions`` shows a form component in a
    modal, and a ``ModelCrudScrollComponent.PageFormOptions`` sends the user
    to a page. Left as ``None``, the list has no create or edit.

    ``item_delete_options`` says how a row is deleted: a
    ``ModelCrudScrollComponent.DeleteOptions`` shows a confirmation component
    in a modal, and a ``ModelCrudScrollComponent.PageDeleteOptions`` sends the
    user to a page. The default is a confirmation that soft-deletes the row
    with ``set_deleted()``. Left as ``None``, the list has no delete.

    Only rows in ``get_queryset()`` can be edited or deleted. The browser
    fetches the form and the confirmation with ``load_item_form()`` and
    ``load_item_delete_confirmation()``, which check the user's access and
    that the row is in the list. Customise an action through the two settings
    and ``get_queryset()``, which keep those checks, and not by overriding the
    callables.
    """

    DeleteOptions = delete_options.DeleteOptions
    PageDeleteOptions = delete_options.PageDeleteOptions
    FormOptions = form_options.FormOptions
    PageFormOptions = form_options.PageFormOptions

    template = 'django_spire/component/scroll/crud_scroll.html'
    item_delete_options: ClassVar[DeleteOptions | PageDeleteOptions | None] = DeleteOptions()
    item_form_options: ClassVar[FormOptions | PageFormOptions | None] = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if cls.item_delete_options is not None and not isinstance(
            cls.item_delete_options,
            cls.DeleteOptions | cls.PageDeleteOptions,
        ):
            message = (
                f'{cls.__name__}.item_delete_options must be a '
                'ModelCrudScrollComponent.DeleteOptions, a '
                'ModelCrudScrollComponent.PageDeleteOptions, or None.'
            )
            raise ImproperlyConfigured(message)

        if cls.item_form_options is not None and not isinstance(
            cls.item_form_options,
            cls.FormOptions | cls.PageFormOptions,
        ):
            message = (
                f'{cls.__name__}.item_form_options must be a '
                'ModelCrudScrollComponent.FormOptions, a '
                'ModelCrudScrollComponent.PageFormOptions, or None.'
            )
            raise ImproperlyConfigured(message)

    @Glue.attr(required_access=Glue.Access.DELETE)
    def load_item_delete_confirmation(self, pk: int | str) -> BaseModelDeleteConfirmationComponent:
        if not isinstance(self.item_delete_options, self.DeleteOptions):
            message = f'{type(self).__name__} has no confirmation component to delete a row with.'
            raise PermissionDenied(message)

        return self.item_delete_options.component(
            instance=self.get_instance(pk),
            access=self.access,
        )

    @Glue.attr(required_access=Glue.Access.CHANGE)
    def load_item_form(self, pk: int | str | None = None) -> ModelFormComponent:
        if not isinstance(self.item_form_options, self.FormOptions):
            message = f'{type(self).__name__} has no form component to create or edit a row with.'
            raise PermissionDenied(message)

        if pk is not None:
            self.get_instance(pk)

        return self.item_form_options.build_component(pk=pk, access=self.access)
