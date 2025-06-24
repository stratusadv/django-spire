import json

from django.db.models import Q

from django_spire.core.filtering.constants import NOT_SELECTED_CHOICES


# Used for boolean fields filtered with select field.
def query_bool_select_field(
        query: Q,
        field_name: str,
        field_value: str | None
) -> Q:
    if field_value in NOT_SELECTED_CHOICES:
        return query

    if isinstance(field_value, str):
        field_value = json.loads(field_value)

    query &= Q(**{field_name: bool(field_value)})

    return query


def query_multi_select_field(
        query: Q,
        field_name: str,
        field_value: list[str] | str
) -> Q:
    if not field_value:
        return query

    if isinstance(field_value, str):
        field_value = json.loads(field_value)

    field_values = [
        value for value in field_value
        if value not in NOT_SELECTED_CHOICES
    ]

    if field_values:
        query &= Q(**{field_name + '__in': field_values})

    return query


def query_select_field(
        query: Q,
        field_name: str,
        field_value: str | None,
) -> Q:
    if field_value not in NOT_SELECTED_CHOICES:
        query &= Q(**{field_name: field_value})

    return query
