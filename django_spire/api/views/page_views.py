from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.urls import reverse

from django_spire.api.models import ApiAccess
from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.generic_views import portal_views

if TYPE_CHECKING:
    from django.http import HttpResponseRedirect
    from django.template.response import TemplateResponse
    from django.core.handlers.wsgi import WSGIRequest

    from django_spire.contrib.breadcrumb import Breadcrumbs


@AppAuthController('api').permission_required('can_view')
def access_list_view(request: WSGIRequest) -> TemplateResponse:
    def breadcrumbs_func(breadcrumbs: Breadcrumbs) -> None:
        breadcrumbs.add_breadcrumb(name='Api Access')

    return portal_views.list_view(
        request,
        model=ApiAccess,
        breadcrumbs_func=breadcrumbs_func,
        context_data={
            'api_accesses': ApiAccess.objects.active(),
        },
        template='django_spire/api/page/access_list_page.html',
    )

@AppAuthController('api').permission_required('can_delete')
def access_delete_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect | TemplateResponse:
    ticket = get_object_or_404(ApiAccess, pk=pk)

    return portal_views.delete_form_view(
        request=request,
        obj=ticket,
        return_url=request.GET.get(
            'return_url',
            reverse('django_spire:api:page:list')
        )
    )
