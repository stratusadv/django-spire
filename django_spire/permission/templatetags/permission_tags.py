from __future__ import annotations

from django import template


register = template.Library()


@register.simple_tag
def check_permission(user, app_label: str, model_name: str, action: str):
    return user.has_perm(f'{app_label}.{action}_{model_name}')
