from __future__ import annotations

from django_spire.auth.group.models import AuthGroup


def bulk_create_groups_from_names(names: list[str]) -> list[AuthGroup]:
    existing_groups = set(AuthGroup.objects.all().values_list('name', flat=True))
    seen_names = set()

    new_groups = []

    for name in names:
        if name in existing_groups or name in seen_names:
            continue

        sanitized_name = name.replace('\x00', '')

        if sanitized_name in existing_groups or sanitized_name in seen_names:
            continue

        seen_names.add(sanitized_name)
        new_groups.append(AuthGroup(name=sanitized_name))

    return AuthGroup.objects.bulk_create(new_groups)
