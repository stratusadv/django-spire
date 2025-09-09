from __future__ import annotations

import json
from typing import TYPE_CHECKING


from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django_spire.knowledge.entry.models import Entry


class EntryTransformationService(BaseDjangoModelService['Entry']):
    obj: Entry

    @staticmethod
    def queryset_to_navigation_list(queryset: QuerySet[Entry]) -> list[dict[str, str]]:
        json_list = []
        for entry in queryset:
            current_version = entry.current_version
            json_list.append(
                {
                    'author': current_version.author.get_full_name(),
                    'delete_url': entry.delete_url,
                    'edit_url': entry.edit_url,
                    'entry_id': entry.pk,
                    'last_edit_datetime': (
                        current_version.last_edit_datetime.strftime('%Y-%m-%d')
                        if current_version.last_edit_datetime else ''
                    ),
                    'name': entry.name,
                    'publish_datetime': (
                        current_version.published_datetime.strftime('%Y-%m-%d')
                        if current_version.published_datetime else ''
                    ),
                    'status': current_version.status,
                    'version_id': current_version.id,
                    'view_url': current_version.view_url,
                }
            )

        return json_list
