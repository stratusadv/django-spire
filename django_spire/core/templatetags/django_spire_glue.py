from __future__ import annotations

from typing import TYPE_CHECKING, overload

from django import template

if TYPE_CHECKING:
    from django.template import Context

register = template.Library()


class GlueFormPath(str):
    """
    Dot-path builder for a Glue form proxy in Django templates.

    Subclasses ``str`` so it passes cleanly into ``django_glue`` template
    filters (``glue_field_value_path``, ``glue_field_metadata_path``) and
    renders as its dotted JS path. Implements ``__getitem__`` rather than
    ``__getattr__`` because Django's template resolver checks subscript lookup
    first, preventing collisions with ``str`` methods like ``title``,
    ``format``, ``count``, ``index``, or ``split``.
    """

    @overload
    def __getitem__(self, key: str) -> GlueFormPath: ...

    @overload
    def __getitem__(self, key: int | slice) -> str: ...

    def __getitem__(self, key: str | int | slice) -> GlueFormPath | str:
        if isinstance(key, str):
            return GlueFormPath(f'{self}.{key}')
        return super().__getitem__(key)


class GlueFormPathNode(template.Node):
    def __init__(
        self,
        name_expression: template.base.FilterExpression,
        target_name: str | None = None,
    ) -> None:
        self.name_expression = name_expression
        self.target_name = target_name

    def render(self, context: Context) -> str:
        form_name = self.name_expression.resolve(context)
        if not form_name:
            return ''

        form_name_str = str(form_name)
        context_key = self.target_name or form_name_str
        context[context_key] = GlueFormPath(form_name_str)
        return ''


@register.tag('glue_form_path')
def glue_form_path(
    parser: template.base.Parser,
    token: template.base.Token,
) -> GlueFormPathNode:
    """
    Bind a :class:`GlueFormPath` into the template context.

    Usage::

        {% glue_form_path glue_form_object_name %}
        {% glue_form_path 'time_entry_form' %}
        {% glue_form_path glue_form_object_name as form %}
    """
    bits = token.split_contents()
    if len(bits) == 2:
        return GlueFormPathNode(parser.compile_filter(bits[1]))
    if len(bits) == 4 and bits[2] == 'as':
        return GlueFormPathNode(parser.compile_filter(bits[1]), target_name=bits[3])

    message = (
        f"{bits[0]!r} tag takes a form name "
        f"({{% {bits[0]} 'time_entry_form' %}}) or an 'as <var>' alias "
        f"({{% {bits[0]} glue_form_object_name as form %}})."
    )
    raise template.TemplateSyntaxError(message)
