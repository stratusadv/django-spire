import re

from django import template

register = template.Library()


@register.filter
def format_to_html(value: str) -> str:
    if not value:
        return '&nbsp;'

    line_break_html = re.sub(r'\n', '<br>', value)
    bolded_html = re.sub(
        r'\*\*(.*?)\*\*', r'<span class="fw-bold">\1</span>',
        line_break_html
    )
    italicized_html = re.sub(
        r'\*(.*?)\*', r'<span class="fst-italic">\1</span>',
        bolded_html
    )
    return re.sub(
        r'~~(.*?)~~', r'<span class="text-decoration-line-through">\1</span>',
        italicized_html
    )
