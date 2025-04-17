from django import template
from django.template.base import TokenType
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

class AccordionNode(template.Node):
    def __init__(self, title_nodes, content_nodes):
        self.title_nodes = title_nodes
        self.content_nodes = content_nodes

    def render(self, context):
        title   = mark_safe(self.title_nodes.render(context).strip())
        content = mark_safe(self.content_nodes.render(context).strip())
        return format_html(
            "Hi Mom <details class='accordion'>"
            "  <summary class='accordion-title'>{}</summary>"
            "  <div class='accordion-body'>{}</div>"
            "</details>",
            title, content
        )

@register.tag("accordion")
def do_accordion(parser, token):
    """
    {% accordion %}
        {% accordion_title %}…{% end_accordion_title %}
        {% accordion_content %}…{% end_accordion_content %}
    {% endaccordion %}
    """
    nodelist_title = nodelist_content = None

    while True:
        tok = parser.next_token()

        # 1 – Ignore newlines, spaces, {{ vars }}, comments, etc.
        if tok.token_type != TokenType.BLOCK:
            continue

        # 2 – Dispatch on the tag name held in tok.contents
        if tok.contents == "accordion_title":
            nodelist_title = parser.parse(("end_accordion_title",))
            parser.delete_first_token()
        elif tok.contents == "accordion_content":
            nodelist_content = parser.parse(("end_accordion_content",))
            parser.delete_first_token()
        elif tok.contents == "endaccordion":
            break
        else:
            raise template.TemplateSyntaxError(
                f"Unknown tag inside accordion: {tok.contents}"
            )

    if not (nodelist_title and nodelist_content):
        raise template.TemplateSyntaxError(
            "accordion tag needs both {% accordion_title %} and "
            "{% accordion_content %} blocks."
        )

    return AccordionNode(nodelist_title, nodelist_content)
