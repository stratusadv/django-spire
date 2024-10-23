import json
import uuid

from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag()
def help_button(help_template, help_title=None):
    help_id = f'help-{uuid.uuid4()}'
    rendered_help_button = render_to_string(
        'core/help/help_button.html',
        {
            'help_id': help_id,
            'help_title': help_title,
        }
    )
    rendered_help_template = render_to_string(
        'core/help/help_modal.html',
        {
            'help_id': help_id,
            'help_title': help_title,
            'help_content': render_to_string(help_template),
        }
    )

    return rendered_help_button + rendered_help_template
