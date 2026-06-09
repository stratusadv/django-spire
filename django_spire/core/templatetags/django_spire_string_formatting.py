from __future__ import annotations

import re
from typing import Any

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


@register.filter
def to_camel_case(value: Any) -> str:
    value = str(value)
    parts = re.sub(r'[\s-]+', ' ', value).split()
    if not parts:
        parts = re.findall(r'[A-Z][a-z]+|[a-z]+', value)
    if not parts:
        return ''
    return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])


@register.filter
def to_camel_case_javascript_safe(value: Any) -> str:
    camel = to_camel_case(value)
    if camel and camel[0].isdigit():
        return '_' + camel
    return camel


@register.filter
def to_snake_case(value: Any) -> str:
    value = str(value)
    s1 = re.sub(r'[\s-]+', '_', value)
    s2 = re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', '_', s1)
    return s2.lower()
