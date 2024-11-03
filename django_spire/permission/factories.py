from __future__ import annotations

from django_spire.permission.models import PortalGroup


def bulk_create_groups_from_names(names: list[str]):
    existing_groups = PortalGroup.objects.all().values_list('name', flat=True)

    new_groups = [
        PortalGroup(name=name)
        for name in names
        if name not in existing_groups
    ]

    return PortalGroup.objects.bulk_create(new_groups)
