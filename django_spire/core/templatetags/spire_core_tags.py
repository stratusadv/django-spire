from __future__ import annotations

import random
import string

from typing import Any, Sequence, TYPE_CHECKING, TypeVar

from django import template
from django.db.models import Model
from django.urls import reverse

if TYPE_CHECKING:
    from django.template import RequestContext


register = template.Library()

T = TypeVar('T', bound=Model)
U = TypeVar('U')


@register.filter
def add_str(str1: str, str2: str) -> str:
    """
    Concatenates two strings.

    :param str1: The first string.
    :param str2: The second string.
    :return: The concatenated string.
    """

    return f'{str1}{str2}'


@register.simple_tag()
def content_type_url(url_name: str, obj: T, **kwargs) -> str:
    """
    Constructs a URL for a given content type using the object's metadata.

    :param url_name: The name of the URL pattern.
    :param obj: A Django model instance whose metadata is used to construct the URL.
    :param kwargs: Additional keyword arguments for URL reversal.
    :return: The reversed URL as a string.
    """

    kwargs['app_label'] = obj._meta.app_label
    kwargs['model_name'] = obj._meta.model_name
    return reverse(url_name, kwargs=kwargs)


@register.filter
def safe_dict_items(dictionary: dict) -> Any:
    """
    Explicitly call .items() on a dictionary, bypassing key lookup.
    Use when the dict has a key named 'items' and you need the method.
    """
    if hasattr(dictionary, 'items'):
        return dictionary.items()
    return []


@register.filter
def in_list(value: str, arg: str) -> bool:
    """
    Checks if a string is present in a comma-separated list.

    :param value: The string to check.
    :param arg: A comma-separated string of values.
    :return: True if the value is present, False otherwise.
    """

    return value in arg.split(',')


@register.filter
def index(indexable: Sequence[U], index_value: int) -> U | Sequence[U]:
    """
    Returns the element at the given index from an indexable or
    the entire indexable if the index is out-of-bounds.

    :param indexable: A sequence from which to retrieve an element.
    :param index_value: The index of the element to retrieve.
    :return: The element at the specified index, or the original sequence
    if the index is out-of-bounds.
    """

    try:
        return indexable[index_value]
    except IndexError:
        return indexable


@register.filter(name='is_path')
def is_path(current: str, url: str) -> bool:
    if not current or not url:
        return False

    if current == url:
        return True

    return url != '/' and current.startswith(url)


@register.simple_tag()
def generate_id() -> str:
    """
    Generates an 8-character random string using ASCII letters.

    :return: An 8-character random string.
    """

    random_string = ''

    for _ in range(8):
        random_string = random_string + random.choice(string.ascii_letters)

    return random_string


@register.filter
def not_in_list(value: str, arg: str) -> bool:
    """
    Checks if a string is not present in a comma-separated list.

    :param value: The string to check.
    :param arg: A comma-separated string of values.
    :return: True if the value is not present, False otherwise.
    """

    return value not in arg.split(',')


@register.simple_tag()
def query_param_url(context: RequestContext, url_name: str, **kwargs) -> str:
    """
    Generates a URL by appending the query parameters from the
    request context to a reversed URL.

    :param context: A RequestContext containing the current request.
    :param url_name: The name of the URL pattern.
    :param kwargs: Additional keyword arguments for URL reversal.
    :return: The generated URL with query parameters appended as a string.
    """

    query_string = '?'

    for index, query_param in enumerate(context.request.GET):
        if index == 0:
            query_string = (
                query_string +
                f'{query_param}={context.request.GET[query_param]}'
            )
        else:
            query_string = (
                query_string +
                f'&{query_param}={context.request.GET[query_param]}'
            )

    return reverse(url_name, kwargs=kwargs) + query_string


@register.simple_tag()
def to_snake_case(label: str) -> str:
    """
    Converts a label to snake_case by replacing spaces with underscores
    and then converting it to lowercase.

    :param label: The label string to convert.
    :return: The snake_case version of the label.
    """

    return label.replace(' ', '_').lower()
