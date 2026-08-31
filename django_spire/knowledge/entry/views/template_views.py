from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse

from django_spire.auth.permissions.decorators import permission_required
from django_spire.knowledge.collection.breadcrumbs import add_collection_chain_breadcrumbs
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.navigation import EntryNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_knowledge.view_collection')
def file_list_view(request: WSGIRequest, collection_pk: int = 0) -> TemplateResponse:
    nav = EntryNavigation()
    nav.page_title = 'Importing Files'

    if collection_pk != 0:
        collection = Collection.objects.select_related('parent').get(pk=collection_pk)

        add_collection_chain_breadcrumbs(nav.breadcrumbs, collection)

        nav.breadcrumbs.add('Importing Files')

    return TemplateResponse(
        request,
        context=nav.as_context() | {'files_json': Entry.services.tool.get_files_to_convert_json()},
        template='django_spire/knowledge/entry/file/page/list_page.html',
    )
