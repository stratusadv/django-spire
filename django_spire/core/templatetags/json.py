from typing import Sequence

from django import template
import json

register = template.Library()


@register.filter(name='to_json')
def to_json(value: dict | Sequence) -> str:
    try:
        return json.dumps(value)
    except (TypeError, ValueError) as e:
        return ''
