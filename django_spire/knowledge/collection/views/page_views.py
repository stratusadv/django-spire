from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.generic_views import portal_views
from django_spire.knowledge.collection.models import Collection


@login_required()
def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    collection = get_object_or_404(Collection, pk=pk)

    return portal_views.delete_form_view(
        request,
        obj=collection,
        return_url=request.GET.get(
            'return_url',
            reverse('django_spire:knowledge:collection:page:list')
        )
    )


@login_required()
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    collection = get_object_or_404(Collection, pk=pk)

    return portal_views.detail_view(
        request,
        obj=collection,
        context_data={
            'collection': collection,
            'current_entries': (
                collection.entries
                .active()
                .has_current_version()
                .user_has_access(user=request.user)
                .select_related('current_version')
                .order_by('order')
            )
        },
        template='django_spire/knowledge/collection/page/detail_page.html'
    )


@login_required()
def list_view(request: WSGIRequest) -> TemplateResponse:
    collections = Collection.objects.active().select_related('parent')

    return portal_views.list_view(
        request,
        model=Collection,
        context_data={
            'collections': collections
        },
        template='django_spire/knowledge/collection/page/list_page.html'
    )
