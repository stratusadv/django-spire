from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.contrib.navigation.breadcrumbs import Breadcrumbs
    from django_spire.knowledge.collection.models import Collection


def add_collection_chain_breadcrumbs(nav_breadcrumbs: Breadcrumbs, collection: Collection) -> None:
    breadcrumbs = []

    temp_collection = collection

    while temp_collection:
        breadcrumbs.append(
            {
                'name': str(temp_collection),
                'view_name': 'django_spire:knowledge:collection:page:top_level',
                'view_kwargs': {'pk': temp_collection.pk},
            }
        )
        temp_collection = temp_collection.parent

    for crumb in reversed(breadcrumbs):
        nav_breadcrumbs.add(**crumb)
