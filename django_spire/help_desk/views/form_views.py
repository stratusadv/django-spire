import django_glue as dg

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.auth.group.decorators import permission_required
from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.generic_views import portal_views
from django_spire.help_desk import forms
from django_spire.help_desk.models import HelpDeskTicket


@permission_required('django_spire_help_desk.change_helpdeskticket')
def ticket_form_view(request, pk: int = 0):
    ticket = get_object_or_null_obj(HelpDeskTicket, pk=pk)

    dg.glue_model_object(request, 'ticket', ticket)

    if request.method == 'POST':
        form = forms.HelpDeskTicketForm(request.POST, instance=ticket)

        if form.is_valid():
            form.save(user=request.user)
            return redirect(reverse('django_spire:help_desk:page:list'))

        show_form_errors(request, form)

    else:
        form = forms.HelpDeskTicketForm(instance=ticket)

    return portal_views.model_form_view(
        request=request,
        obj=ticket,
        template='django_spire/help_desk/page/ticket_form_page.html',
        form=form,
        context_data={'ticket': ticket}
    )