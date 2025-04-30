from __future__ import annotations

from functools import wraps
from typing import Any, TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from django.template import Context


register = template.Library()


DIRECTIVES = (
    'x-bind',
    'x-cloak',
    'x-data',
    'x-effect',
    'x-for',
    'x-html',
    'x-id',
    'x-if',
    'x-ignore',
    'x-init',
    'x-model',
    'x-modelable',
    'x-on',
    'x-ref',
    'x-show',
    'x-teleport',
    'x-text',
    'x-transition'
)


MAGIC = (
    '$data',
    '$dispatch',
    '$el',
    '$id',
    '$nextTick',
    '$refs',
    '$root',
    '$store',
    '$watch'
)


@register.filter(name='lowercase')
def lowercase(value: str) -> str:
    return value.lower()


@register.inclusion_tag('component/subsection/subheader.html')
def title(title: str = "Subheading") -> dict[str, str]:
    return {'title': title}


def alpine(func: callable) -> callable:
    @wraps(func)
    def wrapper(context: Context, *args, **kwargs) -> Any:
        attributes = {}

        keys = kwargs.keys()

        for key in list(keys):
            if key in DIRECTIVES or MAGIC:
                attributes[key] = kwargs.pop(key)

        context.update(kwargs)
        context.update(attributes)

        return func(context, *args, **kwargs)

    return wrapper


@register.inclusion_tag('django_spire/button/brayden_base.html', takes_context=True)
@alpine
def button(context: Context, **_) -> Context:
    return context
