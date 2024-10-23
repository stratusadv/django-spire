import random
import string

from django import template
from django.urls import reverse

register = template.Library()


@register.filter
def add_str(str1, str2):
    return f'{str1}{str2}'


@register.simple_tag()
def content_type_url(url_name, obj, **kwargs):
    kwargs['app_label'] = obj._meta.app_label
    kwargs['model_name'] = obj._meta.model_name
    return reverse(url_name, kwargs=kwargs)


@register.filter
def in_list(value: str, arg: str):
    return value in arg.split(',')


@register.filter
def index(indexable, index_value):
    try:
        return indexable[index_value]
    except IndexError:
        return indexable


@register.simple_tag()
def generate_id():
    random_string = ''
    for i in range(0, 8):
        random_string = random_string + random.choice(string.ascii_letters)
    return random_string


@register.filter
def not_in_list(value, arg):
    return value not in arg.split(',')


@register.simple_tag()
def query_param_url(context, url_name, **kwargs):
    query_string = f'?'

    for index, query_param in enumerate(context.request.GET):
        if index == 0:
            query_string = query_string + f'{query_param}={context.request.GET[query_param]}'
        else:
            query_string = query_string + f'&{query_param}={context.request.GET[query_param]}'

    url = reverse(url_name, kwargs=kwargs)

    return url + query_string


@register.simple_tag()
def to_snake_case(label: str) -> str:
    return label.replace(' ', '_').lower()
