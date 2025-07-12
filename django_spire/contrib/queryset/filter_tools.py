from __future__ import annotations

from django.db.models import QuerySet


def filter_by_lookup_map(
        queryset: QuerySet,
        lookup_map: dict,
        data: dict,
        extra_filters: dict | None = None
):
    """
    Filters a given queryset based on a lookup map and provided data. Additional filters
    can also be applied if provided.

    Parameters:
        queryset (QuerySet): The queryset to be filtered.
        lookup_map (dict): A dictionary mapping input data keys to filtering fields in
            the queryset.
        data (dict): A dictionary containing key-value pairs to filter the queryset.
        extra_filters (list | None): Optional. A list of extra positional filter
            arguments to be applied. Defaults to None.

    Returns:
        QuerySet: The filtered queryset.
    """
    if extra_filters is None:
        extra_filters = {}

    lookup_kwargs = {
        lookup_map[k]: v
        for k, v in data.items()
        if k in lookup_map and v not in (None, "", [])
    } | extra_filters

    return queryset.filter(**lookup_kwargs)
