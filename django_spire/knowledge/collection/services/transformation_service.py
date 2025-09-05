from __future__ import annotations

import json

from django.db.models import QuerySet

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from django_spire.knowledge.collection.models import Collection


class CollectionTransformationService(BaseDjangoModelService['Collection']):
    obj: Collection

    def to_hierarchy_json(self, queryset: QuerySet[Collection]) -> str:
        collections = list(queryset)

        collection_map = {
            collection.pk : {
                'id': collection.pk,
                'name': collection.name,
                'description': collection.description,
                'children': [],
            }
            for collection in collections
        }

        tree = []

        for collection in collections:
            if collection.parent_id:
                collection_map[collection.parent_id]['children'].append(collection_map[collection.pk])
            else:
                tree.append(collection_map[collection.pk])

        return json.dumps(tree)
