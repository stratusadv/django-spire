from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.navigation import EntryNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('knowledge').permission_required('can_view')
def file_list_view(request: WSGIRequest, collection_pk: int = 0) -> TemplateResponse:
    nav = EntryNavigation()
    nav.breadcrumbs.add('Knowledge')

    if collection_pk != 0:
        collection = Collection.objects.select_related('parent').get(pk=collection_pk)

        nav.breadcrumbs.add('Collections', 'django_spire:knowledge:page:home')

        nav.breadcrumbs.add('Importing Files')

    return TemplateResponse(
        request,
        context={'files_json': Entry.services.tool.get_files_to_convert_json(), **nav.as_context()},
        template='django_spire/knowledge/entry/file/page/list_page.html',
    )
