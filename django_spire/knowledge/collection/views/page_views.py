from __future__ import annotations

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.generic_views import portal_views
from django_spire.knowledge.collection.models import Collection


@AppAuthController('knowledge').permission_required('can_delete')
def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    collection = get_object_or_404(Collection, pk=pk)

    return portal_views.delete_form_view(
        request,
        obj=collection,
        delete_func=collection.services.processor.set_deleted,
        return_url=request.GET.get(
            'return_url',
            reverse('django_spire:knowledge:collection:page:list')
        )
    )


@AppAuthController('knowledge').permission_required('can_view')
def list_view(request: WSGIRequest) -> TemplateResponse:
    return portal_views.list_view(
        request,
        model=Collection,
        context_data={},
        template='django_spire/knowledge/collection/page/list_page.html'
    )
