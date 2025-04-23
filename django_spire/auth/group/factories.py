from __future__ import annotations

from django_spire.auth.group.models import AuthGroup


def bulk_create_groups_from_names(names: list[str]):
    existing_groups = AuthGroup.objects.all().values_list('name', flat=True)

    new_groups = [
        AuthGroup(name=name)
        for name in names
        if name not in existing_groups
    ]

    return AuthGroup.objects.bulk_create(new_groups)
