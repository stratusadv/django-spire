from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse

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
            json_list.append(entry.services.transformation.to_dict())

        return json_list

    def to_dict(self):
        site = Site.objects.get_current() if not settings.DEBUG else ''
        current_version = self.obj.current_version

        return {
            'entry_id': self.obj.pk,
            'name': self.obj.name,
            'version_id': current_version.id,
            'author': current_version.author.get_full_name(),
            'last_edit_datetime': (
                current_version.last_edit_datetime.strftime('%Y-%m-%d')
                if current_version.last_edit_datetime else ''
            ),
            'publish_datetime': (
                current_version.published_datetime.strftime('%Y-%m-%d')
                if current_version.published_datetime else ''
            ),
            'status': current_version.status,
            'delete_url': f"""
                {site}{
                    reverse(
                        'django_spire:knowledge:entry:page:delete',
                        kwargs={'pk': self.obj.pk},
                    )
                }
            """,
            'edit_url': f"""
                {site}{
                    reverse(
                        'django_spire:knowledge:entry:form:update',
                        kwargs={
                            'pk': self.obj.pk,
                            'collection_pk': self.obj.collection.pk
                        },
                    )
                }
            """,
            'view_url': f"""
                {site}{
                    reverse(
                        'django_spire:knowledge:entry:version:page:editor',
                        kwargs={'pk': current_version.pk},
                    )
                }
            """,
            'edit_version_url': f"""
                {site}{
                    reverse(
                        'django_spire:knowledge:entry:version:page:editor',
                        kwargs={'pk': current_version.pk},
                    )
                }?view_mode=edit
            """
        }
