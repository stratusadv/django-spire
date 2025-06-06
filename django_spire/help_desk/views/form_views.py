import django_glue as dg
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.forms import Form

from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.generic_views import portal_views
from django_spire.help_desk import forms
from django_spire.help_desk.notifications.handlers import TicketEventNotificationHandler
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.permissions import HelpDeskTicketPermissionHandler


def ticket_delete_form_view(
        request,
        permission_handler=HelpDeskTicketPermissionHandler,
        pk: int = 0
):
    ticket = HelpDeskTicket.objects.get_ticket_detail_for_user(
        permission_handler,
        ticket_pk=pk,
        user=request.user,
    )

    if request.method == 'POST':
        ticket.set_deleted()
        return redirect(reverse('help_desk:page:list'))

    return portal_views.form_view(
        request,
        form=Form(),
        verb=f'Delete',
        obj=ticket,
        template='django_spire/help_desk/page/ticket_form_page.html',
        context_data={
            'ticket_pk': pk,
            'form_action_url': reverse(
                'help_desk:form:delete',
                kwargs={'pk': pk}
            ),
        }
    )


def ticket_create_form_view(
    request,
    permission_handler=HelpDeskTicketPermissionHandler
):
    ticket = HelpDeskTicket()

    dg.glue_model_object(request, 'ticket', ticket)

    if request.method == 'POST':
        form = forms.HelpDeskTicketCreateForm(request.POST)

        if form.is_valid():
            ticket = form.save(user=request.user)
            TicketEventNotificationHandler.handle_new(ticket)

            return redirect(reverse('help_desk:page:list'))

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
            'form_action_url': reverse('help_desk:form:create'),
        }
    )


def ticket_update_form_view(
        request,
        pk: int,
        permission_handler=HelpDeskTicketPermissionHandler
):
    ticket = HelpDeskTicket.objects.get_ticket_detail_for_user(
        ticket_pk=pk,
        user=request.user,
        permission_handler=permission_handler
    )

    dg.glue_model_object(request, 'ticket', ticket)

    if request.method == 'POST':
        form = forms.HelpDeskTicketUpdateForm(request.POST, instance=ticket)

        if form.is_valid():
            ticket = form.save()

            return redirect(reverse('help_desk:page:list'))

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
            'form_action_url': reverse('help_desk:form:update', kwargs={'pk': ticket.pk}),
            'ticket_pk': ticket.pk
        }
    )