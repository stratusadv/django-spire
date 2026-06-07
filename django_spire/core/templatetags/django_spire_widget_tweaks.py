# Copyright (c) 2026 Nathan Johnson - Stratus Advanced Technologies LTD
#
# This file contains modified code derived from django-widget-tweaks:
#
# https://github.com/jazzband/django-widget-tweaks
#
# Copyright (c) 2011-2015 Mikhail Korobov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import annotations

import re
import types
from copy import copy
from typing import TYPE_CHECKING, Any, Callable

from django.template import Library, Node, TemplateSyntaxError

if TYPE_CHECKING:
    from django.forms import BoundField, Widget

    from django.template.base import FilterExpression, Parser, Token

register = Library()


def silence_without_field(function: Callable) -> Callable:
    def wrapped(field: Any, attr: Any) -> Any:
        if not field:
            return ''
        return function(field, attr)

    return wrapped


def _process_field_attributes(
    field: BoundField, attr: str, process: Callable[[Widget, dict[str, Any], str, Any], None]
) -> BoundField:
    params = re.split(r'(?<!:):(?!:)', attr, maxsplit=1)
    attribute = params[0].replace('::', ':')
    value = params[1] if len(params) == 2 else True
    field = copy(field)

    if not hasattr(field, 'as_widget'):
        old_tag = field.tag

        def tag(self, _wrap_label: bool = False) -> str:  # noqa: ANN001
            attrs = self.items['attrs']  # type: ignore[union-attr]
            process(self.parent_widget, attrs, attribute, value)  # type: ignore[union-attr]
            html = old_tag(wrap_label=False)
            self.tag = old_tag  # type: ignore[union-attr]
            return html

        field.tag = types.MethodType(tag, field)
        return field

    old_as_widget = field.as_widget

    def as_widget(
        self,  # noqa: ANN001
        widget: Widget | None = None,
        attrs: dict[str, Any] | None = None,
        only_initial: bool = False,
    ) -> str:
        attrs = attrs or {}
        process(widget or self.field.widget, attrs, attribute, value)
        if attribute == 'type':
            self.field.widget.input_type = value
            del attrs['type']
        html = old_as_widget(widget, attrs, only_initial)
        self.as_widget = old_as_widget
        return html

    field.as_widget = types.MethodType(as_widget, field)
    return field


@register.filter('attr')
@silence_without_field
def set_attr(field: BoundField, attr: str) -> BoundField:
    def process(_widget: Any, attrs: dict[str, Any], attribute: str, value: Any) -> None:
        attrs[attribute] = value

    return _process_field_attributes(field, attr, process)


@register.filter('add_error_attr')
@silence_without_field
def add_error_attr(field: BoundField, attr: str) -> BoundField:
    if hasattr(field, 'errors') and field.errors:
        return set_attr(field, attr)
    return field


@register.filter('append_attr')
@silence_without_field
def append_attr(field: BoundField, attr: str) -> BoundField:
    def process(widget: Any, attrs: dict[str, Any], attribute: str, value: Any) -> None:
        if attrs.get(attribute):
            attrs[attribute] += ' ' + value
        elif widget.attrs.get(attribute):
            attrs[attribute] = widget.attrs[attribute] + ' ' + value
        else:
            attrs[attribute] = value

    return _process_field_attributes(field, attr, process)


@register.filter('add_class')
@silence_without_field
def add_class(field: BoundField, css_class: str) -> BoundField:
    return append_attr(field, 'class:' + css_class)


@register.filter('add_label_class')
@silence_without_field
def add_label_class(field: BoundField, css_class: str) -> str:
    return field.label_tag(attrs={'class': css_class})


@register.filter('add_error_class')
@silence_without_field
def add_error_class(field: BoundField, css_class: str) -> BoundField:
    if hasattr(field, 'errors') and field.errors:
        return add_class(field, css_class)
    return field


@register.filter('add_required_class')
@silence_without_field
def add_required_class(field: BoundField, css_class: str) -> BoundField:
    if hasattr(field.field, 'required') and field.field.required:
        return add_class(field, css_class)
    return field


@register.filter('set_data')
@silence_without_field
def set_data(field: BoundField, data: str) -> BoundField:
    return set_attr(field, 'data-' + data)


@register.filter(name='field_type')
def field_type(field: BoundField) -> str:
    if hasattr(field, 'field') and field.field:
        return field.field.__class__.__name__.lower()
    return ''


@register.filter(name='widget_type')
def widget_type(field: BoundField) -> str:
    if hasattr(field, 'field') and hasattr(field.field, 'widget') and field.field.widget:
        return field.field.widget.__class__.__name__.lower()
    return ''


ATTRIBUTE_RE = re.compile(
    r"""
    (?P<attr>
        [@\w:_\.-]+
    )
    (?P<sign>
        \+?=
    )
    (?P<value>
    ['"]? # start quote
        [^"']*
    ['"]? # end quote
    )
""",
    re.VERBOSE | re.UNICODE,
)


@register.tag
def render_field(parser: Parser, token: Token) -> Node:
    error_msg = (
        f'{token.split_contents()[0]!r} tag requires a form field followed by '
        'a list of attributes and values in the form attr="value"'
    )
    try:
        bits = token.split_contents()
        _ = bits[0]
        form_field = bits[1]
        attr_list = bits[2:]
    except ValueError as exc:
        raise TemplateSyntaxError(error_msg) from exc

    form_field = parser.compile_filter(form_field)

    set_attrs: list[tuple[str, FilterExpression]] = []
    append_attrs: list[tuple[str, FilterExpression]] = []
    for pair in attr_list:
        match = ATTRIBUTE_RE.match(pair)
        if not match:
            raise TemplateSyntaxError(error_msg + f': {pair}')
        dct = match.groupdict()
        attr, sign, value = (dct['attr'], dct['sign'], parser.compile_filter(dct['value']))  # type: ignore[assignment]
        if sign == '=':
            set_attrs.append((attr, value))
        else:
            append_attrs.append((attr, value))

    return FieldAttributeNode(form_field, set_attrs, append_attrs)


class FieldAttributeNode(Node):
    def __init__(
        self,
        field: FilterExpression,
        set_attrs: list[tuple[str, FilterExpression]],
        append_attrs: list[tuple[str, FilterExpression]],
    ) -> None:
        self.field = field
        self.set_attrs = set_attrs
        self.append_attrs = append_attrs

    def render(self, context: Any) -> str:
        bounded_field = self.field.resolve(context)
        field = getattr(bounded_field, 'field', None)
        if getattr(bounded_field, 'errors', None) and 'WIDGET_ERROR_CLASS' in context:
            bounded_field = append_attr(bounded_field, f'class:{context["WIDGET_ERROR_CLASS"]}')
        if field and field.required and 'WIDGET_REQUIRED_CLASS' in context:
            bounded_field = append_attr(bounded_field, f'class:{context["WIDGET_REQUIRED_CLASS"]}')
        for k, v in self.set_attrs:
            if k == 'type':
                bounded_field.field.widget.input_type = v.resolve(context)
            else:
                bounded_field = set_attr(bounded_field, f'{k}:{v.resolve(context)}')
        for k, v in self.append_attrs:
            bounded_field = append_attr(bounded_field, f'{k}:{v.resolve(context)}')
        return str(bounded_field)


@register.filter('remove_attr')
@silence_without_field
def remove_attr(field: BoundField, attr: str) -> BoundField:
    if attr in field.field.widget.attrs:
        del field.field.widget.attrs[attr]
    return field
