from __future__ import annotations

import copy

from django_spire.contrib.seeding.field.enums import FieldSeederTypesEnum


def normalize_seeder_fields(fields: dict) -> dict:
    normalized = {}

    for k, v in fields.items():
        if v in ("exclude", ("exclude",)):
            continue

        if isinstance(v, tuple):
            # Safely clone v[2] if it's a dict
            extra = ()

            if len(v) > 2:
                extra_value = v[2]

                if isinstance(extra_value, dict):
                    extra = (copy.deepcopy(extra_value),)
                else:
                    extra = (extra_value,)

            normalized[k] = (v[0], *v[1:2], *extra)
        elif callable(v):
            normalized[k] = ("callable", v)
        elif isinstance(v, str) and v.lower() in FieldSeederTypesEnum._value2member_map_:
            normalized[k] = (v.lower(),)
        else:
            normalized[k] = ("static", v)

    return normalized
