from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.help_desk.models import HelpDeskTicket

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('help_desk').permission_required('can_delete')
def ticket_delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)
    return_url = request.GET.get('return_url', reverse('django_spire:help_desk:page:list'))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=ticket)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                ticket.set_deleted()
                ticket.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=f'{request.user.get_full_name()} deleted ticket "{ticket}".',
                )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=ticket)

    return TemplateResponse(
        request,
        context={
            'form': form,
            'form_title': f'Delete {ticket}',
            'form_description': f'Are you sure you would like to delete ticket "{ticket}"?',
            'page_title': 'Delete Ticket',
            'breadcrumbs': [
                {'name': 'Help Desk', 'href': reverse('django_spire:help_desk:page:list')},
                {'name': str(ticket), 'href': None},
                {'name': 'Delete', 'href': None},
            ],
        },
        template='django_spire/page/delete_confirmation_form_page.html',
    )


@AppAuthController('help_desk').permission_required('can_view')
def ticket_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)

    context_data = {'ticket': ticket}

    context_data['page_title'] = str(ticket)
    context_data['page_description'] = 'Detail View'
    context_data['breadcrumbs'] = [
        {'name': 'Help Desk', 'href': reverse('django_spire:help_desk:page:list')},
        {'name': str(ticket), 'href': None},
    ]

    return TemplateResponse(
        request,
        context=context_data,
        template='django_spire/help_desk/page/ticket_detail_page.html',
    )


@AppAuthController('help_desk').permission_required('can_view')
def ticket_list_view(request: WSGIRequest) -> TemplateResponse:
    tickets = HelpDeskTicket.objects.order_by('-created_datetime').active()

    context_data = {'tickets': tickets}

    context_data['page_title'] = 'Ticket'
    context_data['page_description'] = 'List View'
    context_data['breadcrumbs'] = [
        {'name': 'Help Desk', 'href': reverse('django_spire:help_desk:page:list')}
    ]

    return TemplateResponse(
        request, context=context_data, template='django_spire/help_desk/page/ticket_list_page.html'
    )
