from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, Http404
from django.shortcuts import get_object_or_404

from django_spire.contrib.generic_views import portal_views
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.permissions import BaseHelpDeskAuthorizationController


@login_required()
def ticket_list_view(
        request: HttpRequest,
        auth_controller: BaseHelpDeskAuthorizationController,
):
    auth = auth_controller.check_authorization(user=request.user)

    if auth.is_helpdesk_admin:
        tickets = HelpDeskTicket.objects.sort_by_date().active()
    else:
        tickets = (HelpDeskTicket.objects
                   .sort_by_date()
                   .active()
                   .filter_by_user(request.user))

    return portal_views.list_view(
        request=request,
        context_data={
            'tickets': tickets,
            'ticket_access': auth.__dict__,
        },
        model=HelpDeskTicket,
        template='django_spire/help_desk/page/ticket_list_page.html'
    )


@login_required()
def ticket_detail_view(
        request,
        pk,
        auth_controller: BaseHelpDeskAuthorizationController,
):
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)
    auth = auth_controller.check_authorization(user=request.user, ticket=ticket)

    if auth.should_deny_ticket_detail_access:
        raise Http404('The ticket could not be retrieved.')

    return portal_views.detail_view(
        request=request,
        obj=ticket,
        context_data={
            'ticket': ticket,
            'ticket_access': auth.__dict__,
        },
        template='django_spire/help_desk/page/ticket_detail_page.html',
    )