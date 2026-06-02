from __future__ import annotations

from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from typing import Any, Iterator

    from django.core.paginator import Page


register = template.Library()


@register.simple_tag(takes_context=True)
def pagination_url(
    context: template.Context,
    page_number: int,
    page_name: str = 'page',
    **kwargs: Any
) -> str:
    updated_context = context.request.GET.copy()
    updated_context[page_name] = page_number
    query_string = '?'

    for index, query_param in enumerate(updated_context):
        query_param_value = updated_context[query_param]
        if isinstance(query_param_value, str):
            # Replacing space with + sign to match how query parameters and django form filtering.
            query_param_value = query_param_value.replace(' ', '+')

        if index == 0:
            query_string = query_string + f'{query_param}={query_param_value}'
        else:
            query_string = query_string + f'&{query_param}={query_param_value}'

    return query_string


@register.simple_tag
def get_elided_page_range(
    page_obj: Page[Any],
    on_each_side: int = 2,
    on_ends: int = 2
) -> Iterator[int | str]:
    return page_obj.paginator.get_elided_page_range(
        number=page_obj.number,
        on_each_side=on_each_side,
        on_ends=on_ends
    )
