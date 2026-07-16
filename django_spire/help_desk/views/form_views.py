from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django_glue import Glue

from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.help_desk import forms
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.navigation import HelpDeskNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    ticket = get_object_or_null_obj(HelpDeskTicket, pk=pk)

    nav = HelpDeskNavigation()
    nav.set_page_title_to_form_action_from_model_instance(ticket)
    nav.breadcrumbs.add('Tickets', 'django_spire:help_desk:page:list')

    if pk:
        nav.breadcrumbs.add(
            name=str(ticket),
            view_name='django_spire:help_desk:page:detail',
            view_kwargs={'pk': ticket.pk},
        )
        nav.breadcrumbs.add('Edit')

    nav.breadcrumbs.add(f'{ticket.description}' if ticket.pk else 'New Ticket (With Glue)')

    form = forms.HelpDeskTicketModelForm(request.POST or None, instance=ticket)

    Glue.form(request, 'ticket_form', form, Glue.Access.DELETE)

    context = {**nav.as_context()}

    return TemplateResponse(
        request=request,
        context=context,
        template='django_spire/help_desk/page/ticket_form_page.html',
    )


@login_required()
def ticket_delete_view(request: WSGIRequest, pk: int) -> TemplateResponse | redirect:
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)
    return_url = request.GET.get('return_url', reverse('django_spire:help_desk:page:list'))

    if request.method == 'POST':
        ticket.set_deleted()

        ticket.add_activity(
            user=request.user,
            verb='deleted',
            information=f'{request.user.get_full_name()} deleted ticket "{ticket}".',
        )

        return redirect(return_url)

    nav = HelpDeskNavigation()
    nav.page_title = f'Delete {ticket.description}'
    nav.breadcrumbs.add('Help Desk', 'django_spire:help_desk:page:list')
    nav.breadcrumbs.add(
        name=str(ticket),
        view_name='django_spire:help_desk:page:detail',
        view_kwargs={'pk': ticket.pk},
    )
    nav.breadcrumbs.add('Delete')

    context = nav.as_context()
    context['ticket'] = ticket
    context['form_title'] = f'Delete {ticket}'
    context['form_description'] = f'Are you sure you would like to delete ticket "{ticket}"?'
    context['return_url'] = return_url

    return TemplateResponse(
        request=request,
        context=context,
        template='django_spire/help_desk/page/ticket_delete_page.html',
    )
