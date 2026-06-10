from __future__ import annotations

from django_glue import Glue
from typing import TYPE_CHECKING

from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.form.tools import show_form_errors

from django_spire.help_desk import forms
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.navigation import HelpDeskNavigation

from django.template.response import TemplateResponse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('help_desk').permission_required('can_add')
def ticket_create_form_view(request: WSGIRequest) -> TemplateResponse:
    ticket = HelpDeskTicket()

    Glue.model(request, 'ticket', ticket)

    if request.method == 'POST':
        form = forms.HelpDeskTicketCreateForm(request.POST)

        if form.is_valid():
            ticket.services.create(created_by=request.user, **form.cleaned_data)
            return redirect(reverse('django_spire:help_desk:page:list'))

        show_form_errors(request, form)

    else:
        form = forms.HelpDeskTicketCreateForm(instance=ticket)

    nav = HelpDeskNavigation()
    nav.page_title = ticket._meta.verbose_name.title()
    nav.page_description = 'Create'
    nav.breadcrumbs.add('Help Desk', reverse('django_spire:help_desk:page:list'))
    nav.breadcrumbs.add('Create', None)
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Create {ticket._meta.verbose_name.title()}'
    context['form_description'] = ''
    context['form_action_url'] = reverse('django_spire:help_desk:form:create')
    return TemplateResponse(request, 'django_spire/help_desk/page/ticket_form_page.html', context)


@AppAuthController('help_desk').permission_required('can_change')
def ticket_update_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)

    Glue.model(request, 'ticket', ticket)

    if request.method == 'POST':
        form = forms.HelpDeskTicketUpdateForm(request.POST, instance=ticket)

        if form.is_valid():
            ticket.services.save_model_obj(**form.cleaned_data)
            return redirect(reverse('django_spire:help_desk:page:list'))

        show_form_errors(request, form)
    else:
        form = forms.HelpDeskTicketUpdateForm(instance=ticket)

    nav = HelpDeskNavigation()
    nav.page_title = ticket._meta.verbose_name.title()
    nav.page_description = 'Edit'
    nav.breadcrumbs.add('Help Desk', reverse('django_spire:help_desk:page:list'))
    nav.breadcrumbs.add(
        str(ticket), reverse('django_spire:help_desk:page:detail', kwargs={'pk': ticket.pk})
    )
    nav.breadcrumbs.add('Edit', None)
    context = nav.as_context()
    context['form'] = form
    context['ticket'] = ticket
    context['form_title'] = f'Edit {ticket._meta.verbose_name.title()} {ticket}'
    context['form_description'] = (
        f'Are you sure you would like to edit {ticket._meta.verbose_name} "{ticket}"?'
    )
    context['form_action_url'] = reverse(
        'django_spire:help_desk:form:update', kwargs={'pk': ticket.pk}
    )
    return TemplateResponse(request, 'django_spire/help_desk/page/ticket_form_page.html', context)
