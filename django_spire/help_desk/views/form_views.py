from __future__ import annotations

import django_glue as dg

from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.generic_views import portal_views
from django_spire.help_desk import forms
from django_spire.help_desk.models import HelpDeskTicket


@AppAuthController('help_desk').permission_required('can_add')
def ticket_create_form_view(request):
    ticket = HelpDeskTicket()

    dg.glue_model_object(request, 'ticket', ticket)

    if request.method == 'POST':
        form = forms.HelpDeskTicketCreateForm(request.POST)

        if form.is_valid():
            ticket.services.create(
                created_by=request.user,
                **form.cleaned_data
            )
            return redirect(reverse('django_spire:help_desk:page:list'))

        show_form_errors(request, form)

    else:
        form = forms.HelpDeskTicketCreateForm(instance=ticket)

    return portal_views.form_view(
        request,
        form=form,
        template='django_spire/help_desk/page/ticket_form_page.html',
        verb='Create',
        obj=ticket,
        context_data={
            'form_action_url': reverse('django_spire:help_desk:form:create'),
        }
    )


@AppAuthController('help_desk').permission_required('can_change')
def ticket_update_form_view(request, pk: int):
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)

    dg.glue_model_object(request, 'ticket', ticket)

    if request.method == 'POST':
        form = forms.HelpDeskTicketUpdateForm(request.POST, instance=ticket)

        if form.is_valid():
            _, _ = ticket.services.save_model_obj(**form.cleaned_data)

            return redirect(reverse('django_spire:help_desk:page:list'))

        show_form_errors(request, form)
    else:
        form = forms.HelpDeskTicketUpdateForm(instance=ticket)

    return portal_views.model_form_view(
        request=request,
        obj=ticket,
        template='django_spire/help_desk/page/ticket_form_page.html',
        form=form,
        context_data={
            'ticket': ticket,
            'form_action_url': (
                reverse('django_spire:help_desk:form:update', kwargs={'pk': ticket.pk})
            ),
        }
    )
