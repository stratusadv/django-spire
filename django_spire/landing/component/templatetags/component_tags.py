from functools import wraps

from django import template


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
def lowercase(value):
    return value.lower()


@register.inclusion_tag('landing/component/subsection/subheader.html')
def title(title="Subheading"):
    return {'title': title}


def alpine(func):
    @wraps(func)
    def wrapper(context, *args, **kwargs):
        attributes = {}

        keys = kwargs.keys()

        for key in list(keys):
            if key in DIRECTIVES or MAGIC:
                attributes[key] = kwargs.pop(key)

        context.update(kwargs)
        context.update(attributes)

        return func(context, *args, **kwargs)

    return wrapper


@register.inclusion_tag('core/button/brayden_base.html', takes_context=True)
@alpine
def button(context, **kwargs):
    return context
