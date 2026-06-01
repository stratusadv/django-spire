from __future__ import annotations

import marko

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def render_markdown(value: str) -> str:
    if not value:
        return ''

    html = marko.convert(value)

    return mark_safe(html)
