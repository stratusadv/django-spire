from __future__ import annotations

from django_glue import Glue
from typing import TYPE_CHECKING

from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.form.tools import show_form_errors
from django_spire.contrib.shortcuts import get_object_or_null_obj

from django_spire.help_desk import forms
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.navigation import HelpDeskNavigation

from django.template.response import TemplateResponse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    ticket = get_object_or_null_obj(HelpDeskTicket, pk=pk)

    nav = HelpDeskNavigation()
    nav.set_page_title_from_model_instance_form_action(ticket)
    nav.breadcrumbs.add(f'{ticket.description}' if ticket.pk else 'New Ticket (With Glue)')

    form = forms.HelpDeskTicketModelForm(request.POST or None, instance=ticket)

    Glue.form(request, 'ticket_form', form, Glue.Access.DELETE)

    context = {**nav.as_context()}

    # nav = HelpDeskNavigation()
    # nav.page_title = ticket._meta.verbose_name.title()
    # nav.page_description = 'Create'
    # nav.breadcrumbs.add('Help Desk', 'django_spire:help_desk:page:list')
    # nav.breadcrumbs.add('Create')
    # context = nav.as_context()
    # context['form'] = form
    # context['form_title'] = f'Create {ticket._meta.verbose_name.title()}'
    # context['form_description'] = ''
    # context['form_action_url'] = reverse('django_spire:help_desk:form:create')
    return TemplateResponse(request=request, context=context, template='django_spire/help_desk/page/ticket_form_page.html')


# @AppAuthController('help_desk').permission_required('can_change')
# def ticket_update_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
#     ticket = get_object_or_404(HelpDeskTicket, pk=pk)
#
#     Glue.model(request, 'ticket', ticket)
#
#     if request.method == 'POST':
#         form = forms.HelpDeskTicketUpdateForm(request.POST, instance=ticket)
#
#         if form.is_valid():
#             ticket.services.save_model_obj(**form.cleaned_data)
#             return redirect(reverse('django_spire:help_desk:page:list'))
#
#         show_form_errors(request, form)
#     else:
#         form = forms.HelpDeskTicketUpdateForm(instance=ticket)
#
#     nav = HelpDeskNavigation()
#     nav.page_title = ticket._meta.verbose_name.title()
#     nav.page_description = 'Edit'
#     nav.breadcrumbs.add('Help Desk', 'django_spire:help_desk:page:list')
#     nav.breadcrumbs.add(
#         str(ticket), 'django_spire:help_desk:page:detail', view_kwargs={'pk': ticket.pk}
#     )
#     nav.breadcrumbs.add('Edit')
#     context = nav.as_context()
#     context['form'] = form
#     context['ticket'] = ticket
#     context['form_title'] = f'Edit {ticket._meta.verbose_name.title()} {ticket}'
#     context['form_description'] = (
#         f'Are you sure you would like to edit {ticket._meta.verbose_name} "{ticket}"?'
#     )
#     context['form_action_url'] = reverse(
#         'django_spire:help_desk:form:update', kwargs={'pk': ticket.pk}
#     )
#     return TemplateResponse(request, 'django_spire/help_desk/page/ticket_form_page.html', context)

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
    nav.breadcrumbs.add(str(ticket))
    nav.breadcrumbs.add('Delete')

    context = nav.as_context()
    context['ticket'] = ticket
    context['form_title'] = f'Delete {ticket}'
    context['form_description'] = f'Are you sure you would like to delete ticket "{ticket}"?'
    return TemplateResponse(
        request=request,
        context=context,
        template='django_spire/help_desk/page/ticket_delete_page.html',
    )