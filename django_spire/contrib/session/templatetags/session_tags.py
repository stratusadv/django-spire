from django import template
from django.utils.html import escapejs
from django.utils.safestring import mark_safe

from django_spire.contrib.session.controller import SessionController

register = template.Library()


@register.simple_tag(takes_context=True)
def session_controller_to_json(context, key):
    request = context.get("request")
    controller = SessionController(request, key)
    data = controller.to_json()
    return mark_safe(escapejs(data))
