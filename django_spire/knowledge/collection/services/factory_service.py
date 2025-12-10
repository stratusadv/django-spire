from __future__ import annotations

from typing import TYPE_CHECKING


from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

    from django_spire.knowledge.collection.models import Collection, CollectionGroup


class CollectionGroupFactoryService(BaseDjangoModelService['CollectionGroup']):
    obj: CollectionGroup

    def replace_groups(
        self,
        request: WSGIRequest,
        group_pks: list[int] | None,
        collection: Collection
    ) -> list[CollectionGroup]:
        if not AppAuthController('knowledge', request).can_change_collection_groups():
            return []

        if group_pks is None:
            return collection.groups.all().delete()

        old_collection_groups = list(collection.groups.all())

        new_collection_groups = [
            self.obj_class(auth_group_id=group_pk, collection=collection)
            for group_pk in group_pks
        ]

        self.obj_class.objects.bulk_create(new_collection_groups)

        for collection in old_collection_groups:
            collection.delete()

        return new_collection_groups
