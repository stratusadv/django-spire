from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django_spire.auth.group.decorators import permission_required
from django_spire.contrib.generic_views import portal_views
from django_spire.help_desk.models import HelpDeskTicket


@permission_required('django_spire_help_desk.delete_helpdeskticket')
def ticket_delete_view(request, pk):
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)

    return portal_views.delete_form_view(
        request=request,
        obj=ticket,
        return_url=request.GET.get(
            'return_url',
            reverse('django_spire:help_desk:page:list')
        )
    )


@login_required()
def ticket_detail_view(request, pk):
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)

    return portal_views.detail_view(
        request=request,
        obj=ticket,
        context_data={
            'ticket': ticket
        },
        template='django_spire/help_desk/page/ticket_detail_page.html',
    )


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
