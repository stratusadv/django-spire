from __future__ import annotations

from typing import TYPE_CHECKING

from django import template
from django.utils.html import escapejs
from django.utils.safestring import mark_safe

from django_spire.contrib.session.controller import SessionController

if TYPE_CHECKING:
    from django.template import Context
    from django.utils.safestring import SafeString


register = template.Library()


@register.simple_tag(takes_context=True)
def session_controller_to_json(context: Context, key: str) -> SafeString:
    request = context.get('request')
    controller = SessionController(request, key)
    data = controller.to_json()
    return mark_safe(escapejs(data))
