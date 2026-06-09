from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.navigation import HelpDeskNavigation

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

    nav = HelpDeskNavigation()
    nav.page_title = 'Delete Ticket'
    nav.breadcrumbs.add_breadcrumb('Help Desk', reverse('django_spire:help_desk:page:list'))
    nav.breadcrumbs.add_breadcrumb(str(ticket), None)
    nav.breadcrumbs.add_breadcrumb('Delete', None)
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {ticket}'
    context['form_description'] = f'Are you sure you would like to delete ticket "{ticket}"?'
    return TemplateResponse(
        request, 'django_spire/contrib/page/delete_confirmation_form_page.html', context=context
    )


@AppAuthController('help_desk').permission_required('can_view')
def ticket_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)

    nav = HelpDeskNavigation()
    nav.page_title = str(ticket)
    nav.page_description = 'Detail View'
    nav.breadcrumbs.add_breadcrumb('Help Desk', reverse('django_spire:help_desk:page:list'))
    nav.breadcrumbs.add_breadcrumb(str(ticket), None)
    context = nav.as_context()
    context['ticket'] = ticket
    return TemplateResponse(
        request, 'django_spire/help_desk/page/ticket_detail_page.html', context=context
    )


@AppAuthController('help_desk').permission_required('can_view')
def ticket_list_view(request: WSGIRequest) -> TemplateResponse:
    tickets = HelpDeskTicket.objects.order_by('-created_datetime').active()

    nav = HelpDeskNavigation()
    nav.page_title = 'Ticket'
    nav.page_description = 'List View'
    nav.breadcrumbs.add_breadcrumb('Help Desk', reverse('django_spire:help_desk:page:list'))
    context = nav.as_context()
    context['tickets'] = tickets
    return TemplateResponse(
        request, 'django_spire/help_desk/page/ticket_list_page.html', context=context
    )
