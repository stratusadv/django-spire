from __future__ import annotations

from typing_extensions import TYPE_CHECKING
from urllib.parse import urlparse

from django.contrib.admin import site
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

if TYPE_CHECKING:
    from django.db.models import Model


EXTERNAL_LINK_SCHEMES = ('http', 'https')


def admin_change_link(instance: Model | None, empty_text: str = '-') -> str:
    url = admin_change_url(instance)

    if url is None:
        return empty_text if instance is None else str(instance)

    return format_html('<a href="{}">{}</a>', url, instance)


def admin_change_url(instance: Model | None) -> str | None:
    if instance is None or instance.pk is None:
        return None

    if not site.is_registered(type(instance)):
        return None

    meta = instance._meta

    return reverse(f'admin:{meta.app_label}_{meta.model_name}_change', args=[instance.pk])


def admin_changelist_url(model_class: type[Model], **filters: str) -> str:
    meta = model_class._meta
    url = reverse(f'admin:{meta.app_label}_{meta.model_name}_changelist')

    if not filters:
        return url

    return f'{url}?{urlencode(filters)}'


def external_link(url: str, text: str, empty_text: str = '-') -> str:
    if not url:
        return empty_text

    if not is_safe_link_url(url):
        return url

    return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>', url, text)


def is_safe_link_url(url: str) -> bool:
    if url.startswith('//'):
        return False

    if url.startswith('/'):
        return True

    return urlparse(url).scheme.lower() in EXTERNAL_LINK_SCHEMES
