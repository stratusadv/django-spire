from __future__ import annotations

from django import template
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe, SafeString


register = template.Library()


@register.simple_tag(takes_context=True)
def define_modal(
    context: RequestContext,
    id: str,
    template: str,
) -> SafeString:
    content = render_to_string(
        template,
        context=context.flatten(),
        request=getattr(context, 'request', None),
    )
    return format_html(
        '<template id="{}" data-spire-modal>{}</template>',
        id,
        mark_safe(content),
    )
