from __future__ import annotations

from django_spire.conf import settings
from django_spire.contrib.utils import get_object_from_module_string
from django_spire.core.search.search import Search


def _resolve_search_class(module_string: str) -> type[Search]:
    search_class = get_object_from_module_string(module_string)

    if not isinstance(search_class, type) or not issubclass(search_class, Search):
        message = f'Search class {module_string} must be a subclass of {Search.__name__}'
        raise TypeError(message)

    return search_class


def get_search_registry() -> dict[str, type[Search]]:
    search_registry: dict[str, type[Search]] = {}

    for search_key, module_string in settings.DJANGO_SPIRE_SEARCH_REGISTRY.items():
        search_registry[search_key] = _resolve_search_class(module_string)

    return search_registry
