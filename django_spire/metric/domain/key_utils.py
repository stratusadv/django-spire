from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils.text import slugify

if TYPE_CHECKING:
    from django.db.models import Model

KEY_MAX_LENGTH = 64


def unique_key_from_name(instance: Model) -> str:
    base = slugify(str(instance.name))[:KEY_MAX_LENGTH] or 'unnamed'
    queryset = instance.__class__._default_manager.filter(key=base)
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    if not queryset.exists():
        return base

    suffix = 2
    while True:
        candidate = f'{base[: KEY_MAX_LENGTH - len(str(suffix))]}-{suffix}'
        if not instance.__class__._default_manager.filter(key=candidate).exists():
            return candidate
        suffix += 1
