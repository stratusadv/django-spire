from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib import Breadcrumbs
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.models import Entry

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('knowledge').permission_required('can_view')
def file_list_view(request: WSGIRequest, collection_pk: int = 0) -> TemplateResponse:
    breadcrumbs = Breadcrumbs()
    breadcrumbs.add_breadcrumb(name='Knowledge')

    if collection_pk != 0:
        collection = Collection.objects.select_related('parent').get(pk=collection_pk)

        breadcrumbs.add_breadcrumb(
            name='Collections',
            href=reverse('django_spire:knowledge:page:home')
        )

        breadcrumbs.add_breadcrumb(name='Importing Files')

    return TemplateResponse(
        request,
        context={
            'files_json': Entry.services.tool.get_files_to_convert_json(),
            'breadcrumbs': breadcrumbs,
        },
        template='django_spire/knowledge/entry/file/page/list_page.html'
    )
