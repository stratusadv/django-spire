from django_spire.seeding.field.enums import FieldSeederTypesEnum


def normalize_seeder_fields(fields: dict) -> dict:
    normalized = {}
    for k, v in fields.items():
        if v == "exclude" or v == ("exclude",):
            continue
        if isinstance(v, tuple):
            normalized[k] = v
        elif callable(v):
            normalized[k] = ("callable", v)
        elif isinstance(v, str) and v.lower() in FieldSeederTypesEnum._value2member_map_:
            normalized[k] = (v.lower(),)
        else:
            normalized[k] = ("static", v)
    return normalized


