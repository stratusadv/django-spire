from __future__ import annotations

import json

from typing import Any, Sequence

from django import template


register = template.Library()


@register.filter(name='to_json')
def to_json(value: dict | Sequence) -> str:
    try:
        return json.dumps(value)
    except (TypeError, ValueError):
        return ''


@register.filter(name='dict_items')
def dict_items(value: Any) -> list[tuple[Any, Any]]:
    if isinstance(value, dict):
        return list(value.items())

    return []
