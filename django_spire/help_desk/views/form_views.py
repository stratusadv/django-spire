import django_glue as dg
from django.http import HttpRequest
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.generic_views import portal_views
from django_spire.help_desk import forms
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.notifications.handlers import TicketEventNotificationHandler


def ticket_delete_form_view(request: HttpRequest, pk: int = 0):
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)

    if request.method == 'POST':
        form = DeleteConfirmationForm(request.POST, obj=ticket)

        if form.is_valid():
            ticket.set_deleted()

            return redirect(reverse('django_spire:help_desk:page:list'))

        show_form_errors(request, form)

    else:
        form = DeleteConfirmationForm(request.GET, obj=ticket)

    return portal_views.form_view(
        request,
        form=form,
        verb=f'Delete',
        obj=ticket,
    )


def ticket_create_form_view(request: HttpRequest):
    ticket = HelpDeskTicket()

    dg.glue_model_object(request, 'ticket', ticket)

    if request.method == 'POST':
        form = forms.HelpDeskTicketCreateForm(request.POST)

        if form.is_valid():
            ticket = form.save(user=request.user)
            TicketEventNotificationHandler.handle_new(ticket)

            return redirect(reverse('django_spire:help_desk:page:list'))

        show_form_errors(request, form)

    else:
        form = forms.HelpDeskTicketCreateForm(instance=ticket)

    return portal_views.form_view(
        request,
        form=form,
        template='django_spire/help_desk/page/ticket_form_page.html',
        verb=f'Create',
        obj=ticket,
        context_data={
            'form_action_url': reverse('django_spire:help_desk:form:create'),
        }
    )


def ticket_update_form_view(request: HttpRequest, pk: int):
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)

    dg.glue_model_object(request, 'ticket', ticket)

    if request.method == 'POST':
        form = forms.HelpDeskTicketUpdateForm(request.POST, instance=ticket)

        if form.is_valid():
            ticket = form.save()

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
            'form_action_url': reverse('django_spire:help_desk:form:update', kwargs={'pk': ticket.pk}),
        }
    )