from django.db.models import QuerySet


def filter_by_lookup_map(queryset: QuerySet, lookup_map: dict, data: dict):
    """
    Filter a queryset using a lookup map that translates input keys to queryset lookup expressions.

    Args:
        queryset: The Django queryset to filter
        lookup_map: A dictionary mapping input keys to queryset lookup expressions 
        data: Dictionary of key-value pairs to filter on

    Returns:
        The filtered queryset based on the lookup map and data
    """
    lookup_kwargs = {
        lookup_map[k]: v
        for k, v in data.items()
        if k in lookup_map and v not in (None, "", [])
    }

    return queryset.filter(**lookup_kwargs)
