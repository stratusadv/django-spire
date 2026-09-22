from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils.text import slugify

if TYPE_CHECKING:
    from django.db.models import Model

KEY_MAX_LENGTH = 64


def unique_key_from_name(instance: Model) -> str:
    parent = getattr(instance, 'domain', None) or getattr(instance, 'group', None)
    temp_key = f'{parent.name}-{instance.name}' if parent else instance.name
    base = slugify(temp_key)[:KEY_MAX_LENGTH] or 'unnamed'
    cleaned_base = base.replace('_', '-')

    queryset = instance.__class__._default_manager.filter(key=cleaned_base)
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    if not queryset.exists():
        return cleaned_base

    suffix = 2
    while True:
        candidate = f'{cleaned_base[: KEY_MAX_LENGTH - len(str(suffix))]}-{suffix}'
        if not instance.__class__._default_manager.filter(key=candidate).exists():
            return candidate
        suffix += 1
