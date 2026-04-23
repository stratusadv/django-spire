from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models.functions import Concat

from django.db.models import F, Value
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_glue import Glue

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.generic_views import portal_views
from django_spire.help_desk.models import HelpDeskTicket

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@AppAuthController('help_desk').permission_required('can_delete')
def ticket_delete_view(request: WSGIRequest, pk: int):
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)

    return portal_views.delete_form_view(
        request=request,
        obj=ticket,
        return_url=request.GET.get(
            'return_url',
            reverse('django_spire:help_desk:page:list')
        )
    )


@AppAuthController('help_desk').permission_required('can_view')
def ticket_detail_view(request: WSGIRequest, pk: int):
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)

    return portal_views.detail_view(
        request=request,
        obj=ticket,
        context_data={
            'ticket': ticket
        },
        template='django_spire/help_desk/page/ticket_detail_page.html',
    )


@AppAuthController('help_desk').permission_required('can_view')
def ticket_list_view(request: WSGIRequest) -> TemplateResponse:
    Glue.queryset(
        request=request,
        target=(
            HelpDeskTicket.objects
            .annotate(
                created_by_name=Concat(
                    'created_by__first_name',
                    Value(' '),
                    'created_by__last_name',
                )
            )
            .select_related('created_by')
            .order_by('-created_datetime')
            .active()
        ),
        unique_name='tickets',
        access=Glue.Access.DELETE,
    )

    return portal_views.list_view(
        request=request,
        model=HelpDeskTicket,
        template='django_spire/help_desk/page/ticket_list_page.html'
    )
