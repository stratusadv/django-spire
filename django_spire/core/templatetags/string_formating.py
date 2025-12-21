from __future__ import annotations

from django import template


register = template.Library()


@register.filter
def dashes_to_underscore(value: str) -> str:
    return value.replace('-', '_')


@register.filter
def spaces_to_underscore(value: str) -> str:
    return value.replace(' ', '_')


@register.filter
def dashes_and_spaces_to_underscore(value: str) -> str:
    return spaces_to_underscore(dashes_to_underscore(value))


@register.filter
def underscores_to_spaces(value: str) -> str:
    return value.replace('_', ' ')
