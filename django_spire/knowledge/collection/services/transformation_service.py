from __future__ import annotations

import json

from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import QuerySet, Prefetch
from django.urls import reverse

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
            queryset.prefetch_related(Prefetch('entries', queryset=entry_queryset))
            .active()
            .order_by('order')
        )

        collection_map = {}
        for collection in collections:
            collection_map[collection.pk] = collection.services.transformation.to_dict()

        tree = []
        for collection in collections:
            if collection.parent_id:
                collection_map[collection.parent_id]['children'].append(
                    collection_map[collection.pk]
                )
            else:
                tree.append(collection_map[collection.pk])

        return json.dumps(tree)

    def to_dict(self):
        site = Site.objects.get_current() if not settings.DEBUG else ''
        entries = self.obj.entries.all()

        return {
            'id': self.obj.pk,
            'name': self.obj.name,
            'description': self.obj.description,
            'children': [],
            'entries': (
                entries.model.services.transformation
                .queryset_to_navigation_list(queryset=entries)
            ),
            'delete_url': f'''
                {site}{
                    reverse(
                        'django_spire:knowledge:collection:page:delete',
                        kwargs={'pk': self.obj.pk},
                    )
                }
            ''',
            'create_entry_url': f'''
                {site}{
                    reverse(
                        'django_spire:knowledge:entry:form:create',
                        kwargs={'collection_pk': self.obj.pk},
                    )
                }
            ''',
            'import_entry_url': f'''
                {site}{
                    reverse(
                        'django_spire:knowledge:entry:form:import',
                        kwargs={'collection_pk': self.obj.pk},
                    )
                }
            ''',
        }
