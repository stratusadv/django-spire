from __future__ import annotations

import json

from django.db.models import QuerySet, Prefetch

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django_spire.knowledge.collection.models import Collection


class CollectionTransformationService(BaseDjangoModelService['Collection']):
    obj: Collection

    @staticmethod
    def to_hierarchy_json(queryset: QuerySet[Collection], user: User) -> str:
        entry_queryset = (
            queryset.model._meta.fields_map.get('entry')
            .related_model
            .objects
            .active()
            .has_current_version()
            .user_has_access(user=user)
            .select_related('current_version__author')
            .order_by('order')
        )

        collections = list(
            queryset.prefetch_related(
                Prefetch('entries', queryset=entry_queryset)
            ).active().order_by('order')
        )

        collection_map = {}
        for collection in collections:
            entries = collection.entries.all()

            collection_map[collection.pk] = {
                'id': collection.pk,
                'name': collection.name,
                'description': collection.description,
                'children': [],
                'delete_url': collection.delete_url,
                'create_entry_url': collection.create_entry_url,
                'import_entry_url': collection.import_entry_url,
                'entries': collection.entries.model.services.transformation.queryset_to_navigation_list(queryset=entries)
        }

        tree = []
        for collection in collections:
            if collection.parent_id:
                collection_map[collection.parent_id]['children'].append(collection_map[collection.pk])
            else:
                tree.append(collection_map[collection.pk])

        return json.dumps(tree)
