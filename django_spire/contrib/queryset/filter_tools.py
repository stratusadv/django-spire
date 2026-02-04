from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import QuerySet, Field, ForeignObjectRel, ForeignKey


def filter_by_lookup_map(
    queryset: QuerySet,
    lookup_map: dict,
    data: dict,
    extra_filters: dict | None = None
):
    """
    Filters a given queryset based on a lookup map and provided data. Additional filters
    can also be applied if provided.

    :param queryset (QuerySet): The queryset to be filtered.
    :param lookup_map (dict): A dictionary mapping input data keys to filtering fields in
        the queryset.
    :param data (dict): A dictionary containing key-value pairs to filter the queryset.
    :param extra_filters (list | None): Optional. A list of extra positional filter
        arguments to be applied. Defaults to None.

    :returns: QuerySet: The filtered queryset.
    """
    if extra_filters is None:
        extra_filters = {}

    lookup_kwargs = {
        lookup_map[k]: v
        for k, v in data.items()
        if k in lookup_map and v not in (None, "", [])
    } | extra_filters

    return queryset.filter(**lookup_kwargs)


def _get_kwarg_name_for_filter_field(
    field: Field[Any, Any] | ForeignObjectRel | GenericForeignKey,
    val: Any
) -> str:
    """
    Determines the appropriate keyword argument name for filtering based on the field type
    and value type.

    :param field (Field | ForeignObjectRel | GenericForeignKey): The model field to generate
        the filter keyword argument for.
    :param val (Any): The value to be used for filtering.

    :returns: str: The keyword argument string suitable for filtering.
    """
    if isinstance(val, Sequence):
        if isinstance(field, ForeignKey):
            return f'{field.name}_id__in'
        return f'{field.name}__in'
    else:
        return field.name


def filter_by_model_fields(queryset: QuerySet, data: dict) -> QuerySet:
    """
    Filters a given queryset based on the queryset's model fields and provided data.

    :param queryset (QuerySet): The queryset to be filtered.
    :param data (dict): A dictionary containing key-value pairs to filter the queryset.

    :returns: QuerySet: The filtered queryset.
    """
    model_fields = [f for f in queryset.model._meta.get_fields()]

    lookup_kwargs = {
        _get_kwarg_name_for_filter_field(
            field=model_field,
            val=data[model_field.name]
        ): data[model_field.name]
        for model_field in model_fields
        if model_field.name in data and data[model_field.name] not in (None, "", [])
    }

    return queryset.filter(**lookup_kwargs)
