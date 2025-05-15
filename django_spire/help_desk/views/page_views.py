from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required

from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.contrib.generic_views import portal_views
import django_glue as dg

@login_required()
def ticket_list_view(request):
    tickets = HelpDeskTicket.objects.order_by('-created_datetime').active()

    return portal_views.list_view(
        request=request,
        context_data={
            'tickets': tickets
        },
        model=HelpDeskTicket,
        template='django_spire/help_desk/page/ticket_list_page.html'
    )

@login_required()
def ticket_detail_view(request, pk):
    ticket = get_object_or_null_obj(HelpDeskTicket, pk=pk)

    return portal_views.detail_view(
        request=request,
        obj=ticket,
        context_data={
            'ticket': ticket
        },
        template='django_spire/help_desk/page/ticket_detail_page.html',
    )