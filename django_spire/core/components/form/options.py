from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from django.core.exceptions import ImproperlyConfigured

from django_spire.core.components.form.model import ModelFormComponent

if TYPE_CHECKING:
    from django.forms import ModelForm


@dataclass(frozen=True, kw_only=True)
class ComponentFormOptions:
    """
    A row is created and edited in a form component, shown in a modal. Give
    the application's own ``component``, or a ``form_class`` with the
    ``template`` that lays out its fields, which the generic
    :class:`ModelFormComponent` shows. The form fires ``saved`` with the
    row's ``pk``.
    """

    component: type[ModelFormComponent] | None = None
    form_class: type[ModelForm] | None = None
    template: str | None = None

    def __post_init__(self) -> None:
        if self.component is not None and (
            self.form_class is not None or self.template is not None
        ):
            message = (
                'ComponentFormOptions takes a component, or a form_class with a template, '
                'not both: a component declares its own form and template.'
            )
            raise ImproperlyConfigured(message)

        if self.component is None and (self.form_class is None or self.template is None):
            message = (
                'ComponentFormOptions needs a component, or a form_class together with a '
                'template.'
            )
            raise ImproperlyConfigured(message)

    def build_component(self, **parameters: Any) -> ModelFormComponent:
        if self.component is not None:
            return self.component(**parameters)

        return ModelFormComponent(
            form_class=self.form_class,
            template=self.template,
            **parameters,
        )


@dataclass(frozen=True)
class PageFormOptions:
    """
    A row is created and edited on a page of its own. ``url_name`` is the
    route that takes the row's key as ``pk``. Creating a row goes to
    ``create_url_name``, which takes no arguments, or when that is left out,
    to ``url_name`` with a ``pk`` of ``0``.

    Each link carries a ``return_url`` for the page to send the user to
    afterwards: the route named by ``return_url_name``, or when that is left
    out, the address the list is shown at. A page that does not read
    ``return_url`` goes wherever it always does.
    """

    url_name: str
    create_url_name: str | None = None
    return_url_name: str | None = None
