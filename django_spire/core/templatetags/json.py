from __future__ import annotations

import json

from typing import Sequence

from django import template


register = template.Library()


@register.filter(name='to_json')
def to_json(value: dict | Sequence) -> str:
    try:
        return json.dumps(value)
    except (TypeError, ValueError):
        return ''
