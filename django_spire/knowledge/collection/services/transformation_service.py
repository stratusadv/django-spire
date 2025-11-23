from __future__ import annotations

import json

from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import Prefetch
from django.urls import reverse

from django_spire.contrib.service import BaseDjangoModelService

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django_spire.knowledge.collection.models import Collection


class CollectionTransformationService(BaseDjangoModelService['Collection']):
    obj: Collection

    def to_hierarchy_json(self, request: WSGIRequest, parent_id: int) -> str:
        collections = (
            self.obj_class.objects
            .active()
            .children(collection_id=parent_id)
            .request_user_has_access(request)
            .select_related('parent')
        )

        entry_queryset = (
            collections.model._meta.fields_map.get('entry')
            .related_model
            .objects
            .active()
            .has_current_version()
            .user_has_access(user=request.user)
            .select_related('current_version__author')
            .order_by('order')
        )

        collections = list(
            collections.prefetch_related(Prefetch('entries', queryset=entry_queryset))
            .active()
            .order_by('order')
        )

        collection_map = {}
        for collection in collections:
            collection_map[collection.pk] = collection.services.transformation.to_dict()

        tree = []
        for collection in collections:
            if collection.parent_id and collection.parent_id in collection_map:
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
            'edit_url': f'''
                {site}{
                    reverse(
                        'django_spire:knowledge:collection:form:update',
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
