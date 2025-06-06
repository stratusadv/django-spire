from django.contrib.auth.decorators import login_required
from django_spire.contrib.generic_views import portal_views
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.permissions import HelpDeskTicketPermissionController


@login_required()
def ticket_list_view(
        request,
        permission_controller=HelpDeskTicketPermissionController
):
    if permission_controller.is_helpdesk_admin(request.user):
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
            'ticket_perms': permission_controller.get_ticket_perms(request.user),
        },
        model=HelpDeskTicket,
        template='django_spire/help_desk/page/ticket_list_page.html'
    )


@login_required()
def ticket_detail_view(
        request,
        pk,
        permission_controller=HelpDeskTicketPermissionController
):
    ticket = HelpDeskTicket.objects.get_ticket_detail_for_user(
        ticket_pk=pk,
        user=request.user,
        permission_controller=permission_controller
    )

    return portal_views.detail_view(
        request=request,
        obj=ticket,
        context_data={
            'ticket': ticket,
            'ticket_perms': permission_controller.get_ticket_perms(request.user),
        },
        template='django_spire/help_desk/page/ticket_detail_page.html',
    )