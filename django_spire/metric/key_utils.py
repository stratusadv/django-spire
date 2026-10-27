from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from django.utils.text import slugify

if TYPE_CHECKING:
    from django.db.models import Model

KEY_MAX_LENGTH = 64
KEY_WORD_SEPARATOR = '-'
KEY_OBJECT_SEPARATOR = '--'
LOCAL_KEY_PATTERN = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
STORAGE_KEY_PATTERN = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*(?:--[a-z0-9]+(?:-[a-z0-9]+)*)*$')


def object_key(*local_keys: str) -> str:
    return KEY_OBJECT_SEPARATOR.join(local_keys)


def validate_local_key(key: Any, kind: str) -> None:
    if not isinstance(key, str) or not key:
        message = f'{kind} key must be a non-empty string, got {key!r}'
        raise ValueError(message)
    if KEY_OBJECT_SEPARATOR in key:
        message = f'{kind} key {key!r} must not contain "{KEY_OBJECT_SEPARATOR}"'
        raise ValueError(message)
    if len(key) > KEY_MAX_LENGTH:
        message = f'{kind} key {key!r} exceeds {KEY_MAX_LENGTH} characters'
        raise ValueError(message)
    if not LOCAL_KEY_PATTERN.fullmatch(key):
        message = f'{kind} key {key!r} must be lowercase letters, digits, and hyphens'
        raise ValueError(message)


def unique_key_base_from_name(instance: Model) -> str:
    parent = getattr(instance, 'domain', None) or getattr(instance, 'group', None)
    temp_key = f'{parent.name}{KEY_WORD_SEPARATOR}{instance.name}' if parent else instance.name
    slug = slugify(temp_key)[:KEY_MAX_LENGTH]
    return re.sub(r'-{2,}', '-', slug.replace('_', '-')).strip('-') or 'unnamed'


def unique_key(base: str, taken: set[str]) -> str:
    key = base
    suffix = 2
    while key in taken:
        key = f'{base[: KEY_MAX_LENGTH - len(str(suffix)) - 1]}{KEY_WORD_SEPARATOR}{suffix}'
        suffix += 1
    return key


def unique_key_from_name(instance: Model) -> str:
    base = unique_key_base_from_name(instance)
    queryset = instance.__class__._default_manager
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)
    taken = set(queryset.filter(key__startswith=base).values_list('key', flat=True))
    return unique_key(base, taken)
