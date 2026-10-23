from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils.text import slugify

if TYPE_CHECKING:
    from django.db.models import Model

KEY_MAX_LENGTH = 64


def unique_key_base_from_name(instance: Model) -> str:
    parent = getattr(instance, 'domain', None) or getattr(instance, 'group', None)
    temp_key = f'{parent.name}-{instance.name}' if parent else instance.name
    base = slugify(temp_key)[:KEY_MAX_LENGTH] or 'unnamed'
    return base.replace('_', '-')


def unique_key(base: str, taken: set[str]) -> str:
    key = base
    suffix = 2
    while key in taken:
        key = f'{base[: KEY_MAX_LENGTH - len(str(suffix))]}-{suffix}'
        suffix += 1
    return key


def unique_key_from_name(instance: Model) -> str:
    base = unique_key_base_from_name(instance)
    queryset = instance.__class__._default_manager
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)
    taken = set(queryset.filter(key__startswith=base).values_list('key', flat=True))
    return unique_key(base, taken)
