from django.template.loader import render_to_string

from django import template

register = template.Library()


@register.simple_block_tag(takes_context=True)
def custom_buttons_dropdown(context, content: str, trigger_icon: str | None = None):
    return render_to_string(
        template_name='django_spire/dropdown/custom_buttons_dropdown.html',
        context={
            'dropdown_content': content,
            'trigger_icon': trigger_icon,
            **context
        }
    )