from __future__ import annotations

from typing import Any, TypedDict, Self, TYPE_CHECKING

from django.urls import reverse

from django_spire.conf import settings
from django_spire.contrib.navigation.tools import form_action_name

if TYPE_CHECKING:
    from django.db.models import Model


class _BreadcrumbDict(TypedDict):
    name: str
    href: str | None


class _Breadcrumb:
    def __init__(
            self, name: str,
            view_name: str | None = None,
            view_kwargs: dict[str, Any] | None = None,
            href: str | None = None,
    ) -> None:
        if view_name is not None and href is not None:
            message = 'Cannot specify both "href" and "view_name" on a breadcrumbs'
            raise ValueError(message)

        self.name = name
        self.view_name = view_name
        self.view_kwargs = view_kwargs
        self._href = href

    @property
    def href(self) -> str | None:
        if self.view_name:
            return reverse(viewname=self.view_name, kwargs=self.view_kwargs)

        return self._href

    def to_dict(self) -> _BreadcrumbDict:
        return {'name': self.name, 'href': self.href}


class Breadcrumbs:
    def __init__(self) -> None:
        self.items: list[_Breadcrumb] = []
        self.index: int = 0

    def __add__(self, other: Breadcrumbs) -> Self:
        self.items += other.items
        return self

    def __iadd__(self, other: Breadcrumbs) -> Self:
        self.items += other.items
        return self

    def __iter__(self) -> Breadcrumbs:
        self.index = 0
        return self

    def __len__(self) -> int:
        return len(self.items)

    def __next__(self) -> _BreadcrumbDict:
        if self.index >= len(self.items):
            raise StopIteration

        breadcrumb_item = self.items[self.index]
        self.index += 1
        return breadcrumb_item.to_dict()

    def __str__(self) -> str:
        return str(self.items)

    def add(
            self, name: str, view_name: str | None = None, view_kwargs: dict[str, Any] | None = None, href: str | None = None
    ) -> None:
        self.items.append(_Breadcrumb(name=name, view_name=view_name, view_kwargs=view_kwargs, href=href))

    def add_model_plural_name(
            self,
            model: type[Model] | Model,
            view_name: str | None = None,
            view_kwargs: dict[str, Any] | None = None,
            href: str | None = None
    ) -> None:
        self.add(name=model._meta.verbose_name_plural.title(), view_name=view_name, view_kwargs=view_kwargs, href=href)

    def add_model_name(
            self,
            model: type[Model] | Model,
            view_name: str | None = None,
            view_kwargs: dict[str, Any] | None = None,
            href: str | None = None
    ) -> None:
        self.add(name=model._meta.verbose_name.title(), view_name=view_name, view_kwargs=view_kwargs, href=href)

    def add_model_instance_string(
            self, model: Model, view_name: str | None = None, view_kwargs: dict[str, Any] | None = None
    ) -> None:
        self.add(name=str(model), view_name=view_name, view_kwargs=view_kwargs)

    def add_model_instance_form_action(self, model: Model) -> None:
        self.add(name=form_action_name(has_pk=model.pk is not None))

    def remove(self, index: int) -> Breadcrumbs:
        del self.items[index]
        return self

    def reverse(self) -> Breadcrumbs:
        self.items.reverse()
        return self

    def as_context(self) -> dict[str, Any]:
        return {'breadcrumbs': self.items}
