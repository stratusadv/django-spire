from __future__ import annotations
from typing import Optional, TypedDict


class BreadcrumbDict(TypedDict):
    name: str
    href: Optional[str]


class BreadcrumbItem:
    def __init__(self, name: str, href: Optional[str] = None):
        self.name = name
        self.href = href

    def to_dict(self) -> BreadcrumbDict:
        return {'name': self.name, 'href': self.href}


class Breadcrumbs:
    def __init__(self, branch_slug: Optional[str] = None):
        self.data: list[BreadcrumbItem] = []
        self.index: int = 0

    def __add__(self, other):
        self.data += other.data
        return self

    def __iter__(self):
        self.index = 0
        return self

    def __str__(self):
        return str(self.data)

    def __len__(self):
        return len(self.data)

    def __next__(self) -> BreadcrumbDict:
        if self.index >= len(self.data):
            raise StopIteration

        breadcrumb_item = self.data[self.index]
        self.index += 1
        return breadcrumb_item.to_dict()

    def add_base_breadcrumb(self, model):
        if hasattr(model, 'base_breadcrumb'):
            self += model.base_breadcrumb()

    def add_breadcrumb(self, name: str, href: Optional[str] = None) -> None:
        breadcrumb_item = BreadcrumbItem(name=name, href=href)
        self.data.append(breadcrumb_item)

    def add_obj_breadcrumbs(self, obj):
        # Expects a breadcrumb object to be returned from the object
        if hasattr(obj, 'breadcrumbs'):
            object_breadcrumbs = obj.breadcrumbs()
            self.data += object_breadcrumbs.data

    def add_form_breadcrumbs(self, obj):
        self.add_obj_breadcrumbs(obj)
        if obj.pk is None:
            self.add_breadcrumb(name=obj._meta.model._meta.verbose_name)
            self.add_breadcrumb(name='Create')
        else:
            self.add_breadcrumb(name='Edit')

    def remove(self, index: int):
        del self.data[index]
        return self

    def reverse(self):
        self.data.reverse()
        return self
