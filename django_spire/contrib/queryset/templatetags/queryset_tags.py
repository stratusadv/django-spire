from typing import Any

from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def session_queryset_filter(
        context,
        session_filter_key: str,
        key_name: str,
        default_value: Any
):
    request = context['request']
    # queryset_filter_session = QuerySetFilterSession(request, session_filter_key)
    # data = queryset_filter_session.get_data(key_name)
    print('hello')
    return default_value
