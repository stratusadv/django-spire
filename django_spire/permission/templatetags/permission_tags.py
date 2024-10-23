from django import template


register = template.Library()


@register.simple_tag
def check_permission(user, app_label, model_name, action):
    return user.has_perm(f'{app_label}.{action}_{model_name}')
