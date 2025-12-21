from __future__ import annotations

from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from typing import Any


register = template.Library()


@register.filter
def is_dict(value: Any) -> bool:
    return isinstance(value, dict)


@register.filter
def is_not_dict(value: Any) -> bool:
    return not is_dict(value)


@register.filter
def is_list(value: Any) -> bool:
    return isinstance(value, list)


@register.filter
def is_not_list(value: Any) -> bool:
    return not is_list(value)


@register.filter
def is_list_or_tuple(value: Any) -> bool:
    return isinstance(value, (list, tuple))


@register.filter
def is_not_list_or_tuple(value: Any) -> bool:
    return not is_list_or_tuple(value)


@register.filter
def is_tuple(value: Any) -> bool:
    return isinstance(value, tuple)


@register.filter
def is_not_tuple(value: Any) -> bool:
    return not is_tuple(value)
